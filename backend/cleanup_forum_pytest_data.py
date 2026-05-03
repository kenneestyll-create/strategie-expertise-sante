"""
Chirurgical cleanup of pytest-generated forum data.

Strategy:
 1. Identify pytest forum_users by pseudo/email patterns.
 2. Cascade-delete topics/replies/reports authored or reported by these users.
 3. Delete the pytest forum_users themselves.
 4. Also match any remaining topics/replies that contain obvious pytest markers
    ("pytest", "Test pytest topic", "Test Topic from API", "Pytest reply",
     "Spam test", "Reply test", "Report test", "Like test").

Real production users/posts (if any) matching none of these patterns are preserved.
"""
import os
import asyncio
import re
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

PSEUDO_PATTERNS = r'^(pytest-|TestUser\d+|AnonUser\d+|anon-)'
EMAIL_PATTERNS = r'(@test\.com$|@example\.com$|^pytest-.*@)'

# Extra markers found in pytest-generated content
TITLE_MARKERS = [
    'Test pytest topic', 'Test Topic from API', 'Reply test',
    'Like test', 'Report test', 'Bad'
]
CONTENT_MARKERS = [
    'Pytest reply', 'Content from pytest', 'This is a test topic created during API testing'
]
REPORT_REASONS = ['Spam test']


async def cleanup():
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    print(f"[cleanup] Connected to DB: {db_name}")

    # --- 1) Identify pytest forum users ---
    users = await db.forum_users.find(
        {}, {'_id': 0, 'id': 1, 'pseudo': 1, 'email': 1}
    ).to_list(length=None)

    pytest_user_ids = set()
    real_user_count = 0
    for u in users:
        p = u.get('pseudo') or ''
        e = u.get('email') or ''
        if re.match(PSEUDO_PATTERNS, p) or (e and re.search(EMAIL_PATTERNS, e)):
            pytest_user_ids.add(u['id'])
        else:
            real_user_count += 1

    print(f"[cleanup] forum_users: {len(users)} total | pytest={len(pytest_user_ids)} | real={real_user_count}")

    # --- 2) Cascade-delete topics/replies/reports by pytest users ---
    topic_ids_to_delete = set()

    if pytest_user_ids:
        topics = await db.forum_topics.find(
            {'author_id': {'$in': list(pytest_user_ids)}}, {'_id': 0, 'id': 1}
        ).to_list(length=None)
        topic_ids_to_delete.update(t['id'] for t in topics)

        res_t = await db.forum_topics.delete_many({'author_id': {'$in': list(pytest_user_ids)}})
        print(f"[cleanup] forum_topics deleted by pytest authors: {res_t.deleted_count}")

        res_r = await db.forum_replies.delete_many({'author_id': {'$in': list(pytest_user_ids)}})
        print(f"[cleanup] forum_replies deleted by pytest authors: {res_r.deleted_count}")

        res_rep = await db.forum_reports.delete_many({'reporter_id': {'$in': list(pytest_user_ids)}})
        print(f"[cleanup] forum_reports deleted by pytest reporters: {res_rep.deleted_count}")

    # --- 3) Delete any lingering items matching known pytest content markers ---
    extra_title = await db.forum_topics.delete_many({
        '$or': [{'title': {'$regex': f'^{re.escape(m)}$'}} for m in TITLE_MARKERS]
    })
    if extra_title.deleted_count:
        print(f"[cleanup] forum_topics deleted by title marker: {extra_title.deleted_count}")

    extra_content = await db.forum_replies.delete_many({
        '$or': [{'content': {'$regex': f'^{re.escape(m)}$'}} for m in CONTENT_MARKERS]
    })
    if extra_content.deleted_count:
        print(f"[cleanup] forum_replies deleted by content marker: {extra_content.deleted_count}")

    extra_reports = await db.forum_reports.delete_many({
        'reason': {'$in': REPORT_REASONS}
    })
    if extra_reports.deleted_count:
        print(f"[cleanup] forum_reports deleted by reason marker: {extra_reports.deleted_count}")

    # Delete orphan replies pointing at deleted pytest topics
    if topic_ids_to_delete:
        orphan_replies = await db.forum_replies.delete_many({'topic_id': {'$in': list(topic_ids_to_delete)}})
        if orphan_replies.deleted_count:
            print(f"[cleanup] forum_replies orphan-deleted (topic removed): {orphan_replies.deleted_count}")
        orphan_reports = await db.forum_reports.delete_many({
            'target_type': 'topic', 'target_id': {'$in': list(topic_ids_to_delete)}
        })
        if orphan_reports.deleted_count:
            print(f"[cleanup] forum_reports orphan-deleted: {orphan_reports.deleted_count}")

    # --- 4) Delete pytest forum users themselves ---
    if pytest_user_ids:
        res_u = await db.forum_users.delete_many({'id': {'$in': list(pytest_user_ids)}})
        print(f"[cleanup] forum_users deleted: {res_u.deleted_count}")

    # --- 5) Final audit ---
    print("\n[cleanup] Final collection counts:")
    for col in ['forum_topics', 'forum_replies', 'forum_users', 'forum_reports']:
        c = await db[col].count_documents({})
        print(f"  {col}: {c}")


if __name__ == '__main__':
    asyncio.run(cleanup())

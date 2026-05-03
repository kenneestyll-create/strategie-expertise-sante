import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { 
  Star, 
  Quote, 
  Send, 
  Loader2,
  CheckCircle,
  MessageSquare,
  Shield
} from 'lucide-react';
import axios from 'axios';
import { SEO } from '@/components/SEO';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const AvisPage = () => {
  const [avis, setAvis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    nom: '',
    situation: '',
    note: 5,
    témoignage: '',
    consent_publication: false,
    consent_data_processing: false
  });

  useEffect(() => {
    fetchAvis();
  }, []);

  const fetchAvis = async () => {
    try {
      const response = await axios.get(`${API}/avis`);
      setAvis(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des avis:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.nom || !formData.témoignage) {
      toast.error("Veuillez remplir tous les champs obligatoires");
      return;
    }
    if (!formData.consent_publication || !formData.consent_data_processing) {
      toast.error("Veuillez valider les consentements obligatoires.");
      return;
    }

    setSubmitting(true);
    try {
      // Map frontend (nom/situation/témoignage) to backend (nom/type_accompagnement/commentaire) + consents
      await axios.post(`${API}/avis`, {
        nom: formData.nom,
        note: formData.note,
        commentaire: formData.témoignage,
        type_accompagnement: formData.situation || null,
        consent_publication: formData.consent_publication,
        consent_data_processing: formData.consent_data_processing
      });
      setSubmitted(true);
      toast.success("Merci pour votre témoignage !");
    } catch (error) {
      console.error('Erreur:', error);
      const detail = error?.response?.data?.detail;
      toast.error(detail || "Une erreur est survenue");
    } finally {
      setSubmitting(false);
    }
  };

  const renderStars = (note) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star 
        key={i} 
        className={`w-5 h-5 ${i < note ? 'text-amber-400 fill-amber-400' : 'text-gray-300'}`} 
      />
    ));
  };

  const StarRating = ({ value, onChange }) => {
    const [hover, setHover] = useState(0);
    
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => onChange(star)}
            onMouseEnter={() => setHover(star)}
            onMouseLeave={() => setHover(0)}
            className="p-1 transition-transform hover:scale-110"
          >
            <Star 
              className={`w-8 h-8 transition-colors ${
                (hover || value) >= star 
                  ? 'text-amber-400 fill-amber-400' 
                  : 'text-gray-300'
              }`}
            />
          </button>
        ))}
      </div>
    );
  };

  return (
    <main className="page-transition pt-20">
      <SEO title="Avis et témoignages" description="Découvrez les témoignages de nos clients accompagnés en maladie professionnelle, AT/MP et MDPH." path="/avis" />
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div className="max-w-2xl">
              <span className="text-sm font-medium text-accent uppercase tracking-wider">Témoignages</span>
              <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="avis-title">
                Livre d'or
              </h1>
              <p className="text-lg text-muted-foreground">
                Découvrez les témoignages des personnes que j'ai accompagnées. 
                Votre avis compte et peut aider d'autres personnes dans la même situation.
              </p>
            </div>
            <Button 
              size="lg" 
              className="rounded-full px-8 gap-2"
              onClick={() => setShowForm(true)}
              data-testid="laisser-avis-button"
            >
              <MessageSquare className="w-4 h-4" />
              Laisser un avis
            </Button>
          </div>
        </div>
      </section>

      {/* Avis Section */}
      <section className="section-padding">
        <div className="max-w-5xl mx-auto">
          {loading ? (
            <div className="text-center py-12" data-testid="avis-loading">
              <Loader2 className="w-8 h-8 animate-spin mx-auto text-muted-foreground" />
              <p className="mt-4 text-muted-foreground">Chargement des témoignages...</p>
            </div>
          ) : avis.length === 0 ? (
            <div className="text-center py-12">
              <Quote className="w-12 h-12 text-muted-foreground/50 mx-auto mb-4" />
              <p className="text-muted-foreground">
                Aucun témoignage pour le moment. Soyez le premier à partager votre expérience !
              </p>
              <Button 
                className="mt-6 rounded-full"
                onClick={() => setShowForm(true)}
              >
                Laisser un avis
              </Button>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 gap-6" data-testid="avis-list">
              {avis.map((item, index) => (
                <Card key={item.id} className="border-border" data-testid={`avis-item-${index}`}>
                  <CardContent className="p-6">
                    <div className="flex items-center gap-1 mb-4">
                      {renderStars(item.note)}
                    </div>
                    <Quote className="w-8 h-8 text-accent/20 mb-2" />
                    <p className="text-foreground mb-4 italic">
                      "{item.témoignage}"
                    </p>
                    <div className="pt-4 border-t border-border">
                      <p className="font-semibold">{item.nom}</p>
                      {item.situation && (
                        <p className="text-sm text-muted-foreground">{item.situation}</p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Form Dialog */}
      <Dialog open={showForm} onOpenChange={setShowForm}>
        <DialogContent className="max-w-lg">
          {submitted ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="w-8 h-8 text-accent" />
              </div>
              <DialogHeader>
                <DialogTitle>Merci pour votre témoignage !</DialogTitle>
                <DialogDescription className="mt-2">
                  Votre avis a été soumis et sera publié après validation. 
                  Merci de contribuer à aider d'autres personnes.
                </DialogDescription>
              </DialogHeader>
              <Button 
                className="mt-6 rounded-full"
                onClick={() => {
                  setShowForm(false);
                  setSubmitted(false);
                  setFormData({ nom: '', situation: '', note: 5, témoignage: '', consent_publication: false, consent_data_processing: false });
                }}
              >
                Fermer
              </Button>
            </div>
          ) : (
            <>
              <DialogHeader>
                <DialogTitle>Laisser un témoignage</DialogTitle>
                <DialogDescription>
                  Partagez votre expérience pour aider d'autres personnes dans la même situation.
                </DialogDescription>
              </DialogHeader>

              <form onSubmit={handleSubmit} className="space-y-6 mt-4" data-testid="avis-form">
                <div className="space-y-2">
                  <Label>Votre note *</Label>
                  <StarRating 
                    value={formData.note} 
                    onChange={(note) => setFormData(prev => ({ ...prev, note }))}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="nom">Prénom ou pseudonyme *</Label>
                  <Input
                    id="nom"
                    value={formData.nom}
                    onChange={(e) => setFormData(prev => ({ ...prev, nom: e.target.value }))}
                    placeholder="Ex: Marie D. ou AnonymePro"
                    required
                    data-testid="avis-input-nom"
                  />
                  <p className="text-[11px] text-muted-foreground/80">Privilégiez un prénom seul ou un pseudonyme — aucune obligation d'indiquer votre nom complet.</p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="situation">Votre situation (optionnel)</Label>
                  <Input
                    id="situation"
                    value={formData.situation}
                    onChange={(e) => setFormData(prev => ({ ...prev, situation: e.target.value }))}
                    placeholder="Ex: Maladie professionnelle"
                    data-testid="avis-input-situation"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="témoignage">Votre témoignage *</Label>
                  <Textarea
                    id="temoignage"
                    value={formData.témoignage}
                    onChange={(e) => setFormData(prev => ({ ...prev, témoignage: e.target.value }))}
                    placeholder="Partagez votre expérience..."
                    rows={4}
                    required
                    data-testid="avis-input-témoignage"
                  />
                </div>

                {/* RGPD Consent block */}
                <div className="p-4 rounded-lg bg-muted/30 border border-border/60 space-y-3" data-testid="avis-rgpd-block">
                  <div className="flex items-start gap-2 pb-2 border-b border-border/50">
                    <Shield className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" strokeWidth={1.75} />
                    <div className="text-[11px] text-muted-foreground leading-relaxed">
                      Vos données sont collectées par Stratégie & Expertise Santé uniquement pour la publication de votre témoignage. Base légale : consentement (art. 6-1-a RGPD). Durée de conservation : jusqu'à retrait de votre demande. Vous disposez d'un droit d'accès, de rectification et d'effacement — voir notre <Link to="/mentions-legales" className="underline hover:text-accent">politique de confidentialité</Link>.
                    </div>
                  </div>
                  <div className="flex items-start gap-2.5">
                    <Checkbox
                      id="consent-publication"
                      checked={formData.consent_publication}
                      onCheckedChange={(v) => setFormData(prev => ({ ...prev, consent_publication: !!v }))}
                      data-testid="avis-consent-publication"
                      className="mt-0.5"
                    />
                    <Label htmlFor="consent-publication" className="text-xs leading-relaxed cursor-pointer font-normal text-muted-foreground">
                      <span className="text-destructive">*</span> J'autorise la publication de mon témoignage sur le site (prénom/pseudo, note, situation et texte).
                    </Label>
                  </div>
                  <div className="flex items-start gap-2.5">
                    <Checkbox
                      id="consent-data"
                      checked={formData.consent_data_processing}
                      onCheckedChange={(v) => setFormData(prev => ({ ...prev, consent_data_processing: !!v }))}
                      data-testid="avis-consent-data"
                      className="mt-0.5"
                    />
                    <Label htmlFor="consent-data" className="text-xs leading-relaxed cursor-pointer font-normal text-muted-foreground">
                      <span className="text-destructive">*</span> Je consens au traitement de mes données conformément à la politique de confidentialité (incluant, le cas échéant, une information sur ma situation de santé).
                    </Label>
                  </div>
                </div>

                <p className="text-xs text-muted-foreground">
                  Votre témoignage sera publié après validation par l'administrateur.
                </p>

                <Button 
                  type="submit" 
                  className="w-full rounded-lg gap-2"
                  disabled={submitting || !formData.consent_publication || !formData.consent_data_processing}
                  data-testid="avis-submit-button"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Envoi en cours...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      Envoyer mon témoignage
                    </>
                  )}
                </Button>
              </form>
            </>
          )}
        </DialogContent>
      </Dialog>
    </main>
  );
};

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Lock, UserPlus, Shield, Eye, EyeOff, Loader2, CheckCircle, Users } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

export const AdminSettingsTab = ({ axiosConfig }) => {
  // Change password state
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showOld, setShowOld] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [changingPwd, setChangingPwd] = useState(false);

  // Create admin state
  const [newAdminEmail, setNewAdminEmail] = useState('');
  const [newAdminPassword, setNewAdminPassword] = useState('');
  const [newAdminNom, setNewAdminNom] = useState('');
  const [showAdminPwd, setShowAdminPwd] = useState(false);
  const [creatingAdmin, setCreatingAdmin] = useState(false);

  // Admin list
  const [admins, setAdmins] = useState([]);

  useEffect(() => {
    axios.get(`${API}/admin/list-admins`, axiosConfig)
      .then(res => setAdmins(res.data))
      .catch(() => {});
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      toast.error("Les nouveaux mots de passe ne correspondent pas");
      return;
    }
    if (newPassword.length < 8) {
      toast.error("Le mot de passe doit contenir au moins 8 caractères");
      return;
    }
    setChangingPwd(true);
    try {
      await axios.put(`${API}/admin/change-password`, {
        old_password: oldPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      }, axiosConfig);
      toast.success("Mot de passe modifié avec succès");
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur lors du changement de mot de passe");
    } finally {
      setChangingPwd(false);
    }
  };

  const handleCreateAdmin = async (e) => {
    e.preventDefault();
    if (!newAdminEmail || !newAdminPassword) {
      toast.error("Email et mot de passe requis");
      return;
    }
    if (newAdminPassword.length < 8) {
      toast.error("Le mot de passe doit contenir au moins 8 caractères");
      return;
    }
    setCreatingAdmin(true);
    try {
      await axios.post(`${API}/admin/create-admin`, {
        email: newAdminEmail,
        password: newAdminPassword,
        nom: newAdminNom || 'Administrateur',
      }, axiosConfig);
      toast.success(`Compte ${newAdminEmail} créé avec succès`);
      setNewAdminEmail('');
      setNewAdminPassword('');
      setNewAdminNom('');
      // Refresh list
      const res = await axios.get(`${API}/admin/list-admins`, axiosConfig);
      setAdmins(res.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur lors de la création du compte");
    } finally {
      setCreatingAdmin(false);
    }
  };

  return (
    <div className="grid gap-6 lg:grid-cols-2" data-testid="settings-tab">
      {/* Change Password */}
      <Card>
        <CardHeader className="pb-4">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Lock className="w-4 h-4 text-[#C9A84C]" />
            Changer le mot de passe
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleChangePassword} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="old-pwd" className="text-xs">Mot de passe actuel</Label>
              <div className="relative">
                <Input
                  id="old-pwd"
                  type={showOld ? 'text' : 'password'}
                  value={oldPassword}
                  onChange={e => setOldPassword(e.target.value)}
                  required
                  data-testid="old-password-input"
                />
                <button type="button" onClick={() => setShowOld(!showOld)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                  {showOld ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="new-pwd" className="text-xs">Nouveau mot de passe</Label>
              <div className="relative">
                <Input
                  id="new-pwd"
                  type={showNew ? 'text' : 'password'}
                  value={newPassword}
                  onChange={e => setNewPassword(e.target.value)}
                  required
                  minLength={8}
                  data-testid="new-password-input"
                />
                <button type="button" onClick={() => setShowNew(!showNew)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                  {showNew ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="confirm-pwd" className="text-xs">Confirmer le nouveau mot de passe</Label>
              <Input
                id="confirm-pwd"
                type="password"
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                required
                minLength={8}
                data-testid="confirm-password-input"
              />
              {newPassword && confirmPassword && newPassword !== confirmPassword && (
                <p className="text-xs text-red-500">Les mots de passe ne correspondent pas</p>
              )}
              {newPassword && confirmPassword && newPassword === confirmPassword && (
                <p className="text-xs text-emerald-600 flex items-center gap-1"><CheckCircle className="w-3 h-3" /> Mots de passe identiques</p>
              )}
            </div>
            <Button type="submit" disabled={changingPwd || !oldPassword || !newPassword || newPassword !== confirmPassword} className="w-full gap-2" data-testid="change-password-btn">
              {changingPwd ? <><Loader2 className="w-4 h-4 animate-spin" /> Modification...</> : <><Lock className="w-4 h-4" /> Modifier le mot de passe</>}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Create Admin */}
      <Card>
        <CardHeader className="pb-4">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <UserPlus className="w-4 h-4 text-[#C9A84C]" />
            Créer un compte administrateur
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCreateAdmin} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="admin-nom" className="text-xs">Nom</Label>
              <Input
                id="admin-nom"
                type="text"
                value={newAdminNom}
                onChange={e => setNewAdminNom(e.target.value)}
                placeholder="Administrateur"
                data-testid="new-admin-nom-input"
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="admin-email" className="text-xs">Email</Label>
              <Input
                id="admin-email"
                type="email"
                value={newAdminEmail}
                onChange={e => setNewAdminEmail(e.target.value)}
                required
                placeholder="admin@strategie-expertise-sante.fr"
                data-testid="new-admin-email-input"
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="admin-pwd" className="text-xs">Mot de passe</Label>
              <div className="relative">
                <Input
                  id="admin-pwd"
                  type={showAdminPwd ? 'text' : 'password'}
                  value={newAdminPassword}
                  onChange={e => setNewAdminPassword(e.target.value)}
                  required
                  minLength={8}
                  data-testid="new-admin-password-input"
                />
                <button type="button" onClick={() => setShowAdminPwd(!showAdminPwd)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                  {showAdminPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <Button type="submit" disabled={creatingAdmin || !newAdminEmail || !newAdminPassword} className="w-full gap-2" data-testid="create-admin-btn">
              {creatingAdmin ? <><Loader2 className="w-4 h-4 animate-spin" /> Création...</> : <><UserPlus className="w-4 h-4" /> Créer le compte</>}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Admin List */}
      <Card className="lg:col-span-2">
        <CardHeader className="pb-4">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Users className="w-4 h-4 text-[#C9A84C]" />
            Comptes administrateurs ({admins.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {admins.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">Aucun compte trouvé</p>
          ) : (
            <div className="space-y-2">
              {admins.map((a, i) => (
                <div key={a.email || i} className="flex items-center gap-3 p-3 rounded-lg bg-muted/30 border" data-testid={`admin-account-${i}`}>
                  <Shield className="w-4 h-4 text-[#C9A84C]" />
                  <div>
                    <p className="text-sm font-medium">{a.nom || 'Administrateur'}</p>
                    <p className="text-xs text-muted-foreground">{a.email}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

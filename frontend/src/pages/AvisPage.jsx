import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { 
  Star, 
  Quote, 
  Send, 
  Loader2,
  CheckCircle,
  MessageSquare
} from 'lucide-react';
import axios from 'axios';

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
    temoignage: ''
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
    
    if (!formData.nom || !formData.temoignage) {
      toast.error("Veuillez remplir tous les champs obligatoires");
      return;
    }

    setSubmitting(true);
    try {
      await axios.post(`${API}/avis`, formData);
      setSubmitted(true);
      toast.success("Merci pour votre témoignage !");
    } catch (error) {
      console.error('Erreur:', error);
      toast.error("Une erreur est survenue");
    } finally {
      setSubmitting(false);
    }
  };

  const renderStars = (note) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star 
        key={i} 
        className={`w-5 h-5 ${i < note ? 'text-amber-400 fill-amber-400' : 'text-gray-300'}`} 
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
                      "{item.temoignage}"
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
                  setFormData({ nom: '', situation: '', note: 5, temoignage: '' });
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
                  <Label htmlFor="nom">Votre nom ou pseudonyme *</Label>
                  <Input
                    id="nom"
                    value={formData.nom}
                    onChange={(e) => setFormData(prev => ({ ...prev, nom: e.target.value }))}
                    placeholder="Ex: Marie D."
                    required
                    data-testid="avis-input-nom"
                  />
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
                  <Label htmlFor="temoignage">Votre témoignage *</Label>
                  <Textarea
                    id="temoignage"
                    value={formData.temoignage}
                    onChange={(e) => setFormData(prev => ({ ...prev, temoignage: e.target.value }))}
                    placeholder="Partagez votre expérience..."
                    rows={4}
                    required
                    data-testid="avis-input-temoignage"
                  />
                </div>

                <p className="text-xs text-muted-foreground">
                  Votre témoignage sera publié après validation par l'administrateur.
                </p>

                <Button 
                  type="submit" 
                  className="w-full rounded-lg gap-2"
                  disabled={submitting}
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

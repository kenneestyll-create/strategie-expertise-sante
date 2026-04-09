import { useState, useEffect, useRef } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { ArrowRight, Mail, Phone, Clock, CheckCircle, Send, Loader2 } from 'lucide-react';
import axios from 'axios';
import { SEO } from '@/components/SEO';
import { DataConsentBox } from '@/components/DataConsentBox';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const ContactPage = () => {
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [consent, setConsent] = useState(false);
  const [searchParams] = useSearchParams();
  const trackedRef = useRef(false);

  // Extract tracking params from URL
  const trackingVia = searchParams.get('via') || '';
  const trackingSource = searchParams.get('source') || '';
  const trackingCampaign = searchParams.get('campaign') || '';

  // Track contact page visit (once)
  useEffect(() => {
    if (trackedRef.current) return;
    if (!trackingVia && !trackingSource) return;
    trackedRef.current = true;
    axios.post(`${API}/tracking/contact-visit`, {
      via: trackingVia,
      source: trackingSource,
      campaign: trackingCampaign,
    }).catch(() => {});
  }, [trackingVia, trackingSource, trackingCampaign]);

  const [formData, setFormData] = useState({
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    sujet: '',
    message: '',
    type_accompagnement: ''
  });

  const accompagnementTypes = [
    { value: "analyse_dossier", label: "Analyse de dossier" },
    { value: "préparation_expertise", label: "Préparation à une expertise" },
    { value: "stratégie_atmp", label: "Stratégie AT/MP" },
    { value: "accompagnement_assurance", label: "Accompagnement assurantiel" },
    { value: "autre", label: "Autre / Je ne sais pas" }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSelectChange = (value) => {
    setFormData(prev => ({ ...prev, type_accompagnement: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.nom || !formData.prenom || !formData.email || !formData.sujet || !formData.message) {
      toast.error("Veuillez remplir tous les champs obligatoires");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        ...formData,
        ...(trackingVia && { tracking_via: trackingVia }),
        ...(trackingSource && { tracking_source: trackingSource }),
        ...(trackingCampaign && { tracking_campaign: trackingCampaign }),
      };
      await axios.post(`${API}/contact`, payload);
      setSubmitted(true);
      toast.success("Votre message a été envoyé avec succès !");
    } catch (error) {
      console.error('Erreur lors de l\'envoi:', error);
      toast.error("Une erreur est survenue. Veuillez réessayer.");
    } finally {
      setLoading(false);
    }
  };

  const contactInfo = [
    {
      icon: Mail,
      title: "Email",
      value: "contact@strategie-expertise-sante.fr",
      link: "mailto:contact@strategie-expertise-sante.fr"
    },
    {
      icon: Phone,
      title: "Téléphone",
      value: "07 59 93 60 67",
      link: "tel:+33759936067"
    },
    {
      icon: Clock,
      title: "Disponibilités",
      value: "Du lundi au vendredi, 9h-18h",
      link: null
    }
  ];

  if (submitted) {
    return (
      <main className="page-transition pt-20 min-h-screen flex items-center">
      <SEO title="Contact" description="Contactez Stratégie & Expertise Santé pour une première consultation gratuite de 10 minutes sur votre dossier maladie professionnelle, AT/MP ou MDPH." path="/contact" />
        <div className="max-w-2xl mx-auto px-4 text-center py-20">
          <div className="w-20 h-20 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10 text-accent" strokeWidth={1.5} />
          </div>
          <h2 className="text-3xl sm:text-4xl font-semibold mb-4" data-testid="contact-success-title">
            Message envoyé !
          </h2>
          <p className="text-muted-foreground mb-8">
            Merci pour votre message. Je vous recontacterai dans les plus brefs délais, 
            généralement sous 24 à 48 heures.
          </p>
          <Link to="/">
            <Button variant="outline" className="rounded-full px-8" data-testid="back-home-button">
              Retour à l'accueil
            </Button>
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="page-transition pt-20">
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Contact</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="contact-title">
              Prenons contact
            </h1>
            <p className="text-lg text-muted-foreground">
              Vous avez des questions ? Vous souhaitez un accompagnement personnalisé ? 
              Remplissez le formulaire ci-dessous et je vous recontacterai rapidement.
            </p>
          </div>
        </div>
      </section>

      {/* Contact Form Section */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-3 gap-12 min-w-0">
            {/* Contact Info */}
            <div className="lg:col-span-1 space-y-6 min-w-0">
              <div>
                <h2 className="text-2xl font-semibold mb-4">Informations</h2>
                <p className="text-muted-foreground mb-8">
                  La première consultation est gratuite (10 minutes) et sans engagement. N'hésitez pas à me contacter 
                  pour discuter de votre situation.
                </p>
              </div>

              {contactInfo.map((info, index) => (
                <Card key={index} className="border-border overflow-hidden">
                  <CardContent className="p-4 flex items-start gap-4 min-w-0">
                    <div className="w-10 h-10 bg-muted rounded-lg flex items-center justify-center flex-shrink-0">
                      <info.icon className="w-5 h-5 text-accent" strokeWidth={1.5} />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm text-muted-foreground">{info.title}</p>
                      {info.link ? (
                        <a 
                          href={info.link} 
                          className="font-medium hover:text-accent transition-colors break-all"
                          style={{ overflowWrap: 'anywhere' }}
                        >
                          {info.value}
                        </a>
                      ) : (
                        <p className="font-medium">{info.value}</p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}

              {/* Image */}
              <div className="hidden lg:block mt-8">
                <div className="aspect-[4/3] rounded-2xl overflow-hidden">
                  <img
                  loading="lazy" 
                    src="https://images.unsplash.com/photo-1651602855717-9f79c72893cc?auto=format&fit=crop&w=800&q=60" 
                    alt="Contact"
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>
            </div>

            {/* Form */}
            <div className="lg:col-span-2">
              <Card className="border-border">
                <CardContent className="p-6 lg:p-8">
                  <form onSubmit={handleSubmit} className="space-y-6" data-testid="contact-form">
                    {/* Name Fields */}
                    <div className="grid sm:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="prenom">Prénom *</Label>
                        <Input
                          id="prenom"
                          name="prenom"
                          value={formData.prenom}
                          onChange={handleInputChange}
                          placeholder="Votre prénom"
                          required
                          data-testid="input-prenom"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="nom">Nom *</Label>
                        <Input
                          id="nom"
                          name="nom"
                          value={formData.nom}
                          onChange={handleInputChange}
                          placeholder="Votre nom"
                          required
                          data-testid="input-nom"
                        />
                      </div>
                    </div>

                    {/* Contact Fields */}
                    <div className="grid sm:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="email">Email *</Label>
                        <Input
                          id="email"
                          name="email"
                          type="email"
                          value={formData.email}
                          onChange={handleInputChange}
                          placeholder="votre@email.fr"
                          required
                          data-testid="input-email"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="telephone">Téléphone</Label>
                        <Input
                          id="telephone"
                          name="telephone"
                          type="tel"
                          value={formData.telephone}
                          onChange={handleInputChange}
                          placeholder="06 00 00 00 00"
                          data-testid="input-telephone"
                        />
                      </div>
                    </div>

                    {/* Type d'accompagnement */}
                    <div className="space-y-2">
                      <Label htmlFor="type_accompagnement">Type d'accompagnement souhaité</Label>
                      <Select onValueChange={handleSelectChange} data-testid="select-type">
                        <SelectTrigger id="type_accompagnement" data-testid="select-type-trigger">
                          <SelectValue placeholder="Sélectionnez un type d'accompagnement" />
                        </SelectTrigger>
                        <SelectContent>
                          {accompagnementTypes.map((type) => (
                            <SelectItem 
                              key={type.value} 
                              value={type.value}
                              data-testid={`select-option-${type.value}`}
                            >
                              {type.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Sujet */}
                    <div className="space-y-2">
                      <Label htmlFor="sujet">Sujet *</Label>
                      <Input
                        id="sujet"
                        name="sujet"
                        value={formData.sujet}
                        onChange={handleInputChange}
                        placeholder="L'objet de votre demande"
                        required
                        data-testid="input-sujet"
                      />
                    </div>

                    {/* Message */}
                    <div className="space-y-2">
                      <Label htmlFor="message">Message *</Label>
                      <Textarea
                        id="message"
                        name="message"
                        value={formData.message}
                        onChange={handleInputChange}
                        placeholder="Décrivez brièvement votre situation et vos besoins..."
                        rows={6}
                        required
                        data-testid="input-message"
                      />
                    </div>

                    {/* Privacy Notice */}
                    <DataConsentBox checked={consent} onChange={setConsent} variant="informations" />

                    {/* Submit Button */}
                    <Button 
                      type="submit" 
                      size="lg" 
                      className="w-full sm:w-auto rounded-full px-8 gap-2"
                      disabled={loading || !consent}
                      data-testid="submit-button"
                    >
                      {loading ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Envoi en cours...
                        </>
                      ) : (
                        <>
                          Envoyer ma demande
                          <Send className="w-4 h-4" />
                        </>
                      )}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
};

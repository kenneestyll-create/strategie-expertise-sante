import { useState, useEffect, useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import {
  Calendar as CalendarIcon,
  Clock,
  Phone,
  CheckCircle,
  ArrowRight,
  ArrowLeft,
  Loader2,
  ChevronLeft,
  ChevronRight,
  Zap,
  CreditCard,
  Shield,
  Gift,
} from 'lucide-react';
import axios from 'axios';
import { SEO } from '@/components/SEO';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const DAYS_FR = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'];
const MONTHS_FR = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];

const CALL_INFO = {
  decouverte: {
    title: "Appel Découverte",
    subtitle: "Premier contact gratuit",
    duration: "10 min",
    price: null,
    priceLabel: "Gratuit",
    description: "Premier échange court de 10 minutes pour comprendre votre situation et vous orienter vers la solution adaptée.",
    note: "Cet appel ne constitue pas une consultation complète.",
    icon: Gift,
    color: "emerald",
    badge: "1 seul par personne",
  },
  conseil: {
    title: "Appel Conseil",
    subtitle: "Échange structuré sur rendez-vous",
    duration: "30 min",
    price: 75,
    priceLabel: "75 €",
    description: "Échange structuré et ciblé pour faire le point sur votre situation, clarifier vos options et vous orienter avec précision.",
    note: "Ce rendez-vous permet un échange structuré et ciblé sur votre situation.",
    icon: Phone,
    color: "accent",
    badge: "Paiement avant confirmation",
  },
  urgence: {
    title: "Appel Urgence",
    subtitle: "Prioritaire — réponse rapide",
    duration: "Sous 2h ou 30min",
    price: null,
    priceLabel: "Dès 50 €",
    description: "Réponse prioritaire pour les situations nécessitant une prise de contact rapide dans un délai court.",
    note: "Ce format est réservé aux situations nécessitant une prise de contact prioritaire.",
    icon: Zap,
    color: "orange",
    badge: "Traitement prioritaire",
  },
};

export const AgendaPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [step, setStep] = useState('choose');
  const [callType, setCallType] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [booked, setBooked] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [form, setForm] = useState({ name: '', email: '', phone: '', message: '' });
  const [paymentConfirming, setPaymentConfirming] = useState(false);
  const [paymentResult, setPaymentResult] = useState(null);
  const [cgvAccepted, setCgvAccepted] = useState(false);

  const formatDateStr = (date) => {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  };

  // Handle payment return
  useEffect(() => {
    const payment = searchParams.get('payment');
    const sessionId = searchParams.get('session_id');
    const bookingId = searchParams.get('booking_id');
    const typeParam = searchParams.get('type');

    if (typeParam === 'decouverte' && !payment) {
      selectCallType('decouverte');
      const newParams = new URLSearchParams(searchParams);
      newParams.delete('type');
      setSearchParams(newParams, { replace: true });
    }

    if (payment === 'success' && sessionId) {
      setPaymentConfirming(true);
      axios.get(`${API}/bookings/confirm-payment/${sessionId}`)
        .then(res => {
          if (res.data.success) {
            setPaymentResult(res.data);
            setBooked(true);
            setCallType('conseil');
          } else {
            toast.error("Le paiement n'a pas pu être vérifié. Contactez-nous.");
          }
        })
        .catch(() => toast.error("Erreur de vérification du paiement."))
        .finally(() => {
          setPaymentConfirming(false);
          setSearchParams({});
        });
    } else if (payment === 'cancelled') {
      if (bookingId) {
        axios.delete(`${API}/bookings/cancel-pending/${bookingId}`).catch(() => {});
      }
      toast.error("Paiement annulé. Le créneau a été libéré.");
      setSearchParams({});
    }
  }, []);

  const fetchSlots = async (dateStr, type) => {
    setLoadingSlots(true);
    try {
      const res = await axios.get(`${API}/bookings/slots/${dateStr}?call_type=${type}`);
      setAvailableSlots(res.data.slots || []);
    } catch { setAvailableSlots([]); }
    finally { setLoadingSlots(false); }
  };

  const handleDateClick = (date) => {
    setSelectedDate(date);
    setSelectedSlot(null);
    if (callType) fetchSlots(formatDateStr(date), callType);
  };

  const selectCallType = (type) => {
    if (type === 'urgence') {
      window.dispatchEvent(new Event('alerte-urgente:open'));
      return;
    }
    setCallType(type);
    setStep('calendar');
    setSelectedDate(null);
    setSelectedSlot(null);
    setAvailableSlots([]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedDate || !selectedSlot || !form.name || !form.email) {
      toast.error("Veuillez remplir tous les champs obligatoires");
      return;
    }
    setSubmitting(true);

    const payload = {
      date: formatDateStr(selectedDate),
      time_slot: selectedSlot,
      name: form.name,
      email: form.email,
      phone: form.phone,
      message: form.message,
      call_type: callType,
    };

    try {
      if (callType === 'decouverte') {
        await axios.post(`${API}/bookings`, payload);
        setBooked(true);
        toast.success("Rendez-vous confirmé !");
      } else {
        if (!cgvAccepted) {
          toast.error('Veuillez accepter les CGV et la renonciation au droit de rétractation.');
          setSubmitting(false);
          return;
        }
        await axios.post(`${API}/consent-log`, {
          email: form.email, service: `booking_${callType}`, cgv_accepted: true, retractation_waived: true,
        });
        const res = await axios.post(`${API}/bookings/checkout`, {
          ...payload,
          origin_url: window.location.origin,
        });
        if (res.data.url) {
          window.location.href = res.data.url;
        }
      }
    } catch (err) {
      const detail = err.response?.data?.detail || "Erreur lors de la réservation";
      toast.error(detail);
    } finally { setSubmitting(false); }
  };

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const days = [];
    for (let i = 0; i < firstDay; i++) days.push(null);
    for (let i = 1; i <= daysInMonth; i++) days.push(new Date(year, month, i));
    return days;
  };

  const isWeekend = (date) => date && (date.getDay() === 0 || date.getDay() === 6);
  const isPast = (date) => {
    if (!date) return true;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return date < today;
  };
  const isSameDay = (a, b) => a && b && a.toDateString() === b.toDateString();
  const isToday = (date) => date && isSameDay(date, new Date());

  const prevMonth = () => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1));
  const nextMonth = () => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1));

  // Payment confirming state
  if (paymentConfirming) {
    return (
      <main className="page-transition pt-20 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-10 h-10 animate-spin text-accent mx-auto mb-4" />
          <p className="text-lg font-medium">Vérification du paiement en cours...</p>
        </div>
      </main>
    );
  }

  // Booking confirmed
  if (booked) {
    const info = CALL_INFO[callType || 'decouverte'];
    const displayDate = paymentResult?.date || (selectedDate ? selectedDate.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' }) : '');
    const displaySlot = paymentResult?.time_slot || selectedSlot || '';

    return (
      <main className="page-transition pt-20 min-h-screen flex items-center">
        <SEO title="Rendez-vous confirmé" description="Votre rendez-vous est confirmé." path="/agenda" />
        <div className="max-w-2xl mx-auto px-4 text-center py-20">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10 text-green-600" strokeWidth={1.5} />
          </div>
          <h2 className="text-3xl font-semibold mb-2" data-testid="booking-success-title">Rendez-vous confirmé</h2>
          <p className="text-muted-foreground mb-1">
            <strong>{info.title}</strong> — {info.duration}
          </p>
          {(displayDate || displaySlot) && (
            <p className="text-muted-foreground mb-6">
              Le <strong>{displayDate}</strong> à <strong>{displaySlot}</strong>
            </p>
          )}
          {callType === 'conseil' && (
            <p className="text-sm text-green-600 font-medium mb-4">
              <CreditCard className="w-4 h-4 inline mr-1" />
              Paiement confirmé — 75 €
            </p>
          )}
          <p className="text-sm text-muted-foreground mb-8">
            Vous recevrez un email de confirmation avec les détails du rendez-vous.
          </p>
          <Link to="/">
            <Button variant="outline" className="rounded-full px-8">Retour à l'accueil</Button>
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="page-transition pt-20">
      <SEO title="Prendre rendez-vous" description="Réservez un créneau téléphonique avec notre expert. Appel découverte gratuit ou consultation sur rendez-vous." path="/agenda" />

      {/* Header */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Agenda</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-4" data-testid="agenda-title">
              Prendre rendez-vous
            </h1>
            <p className="text-base text-muted-foreground">
              Choisissez le format adapté à votre besoin. Les rendez-vous téléphoniques sont proposés du lundi au vendredi, de 9h à 17h.
            </p>
          </div>
        </div>
      </section>

      {/* Step 1: Choose call type */}
      {step === 'choose' && (
        <section className="section-padding">
          <div className="max-w-5xl mx-auto">
            <div className="grid md:grid-cols-3 gap-5" data-testid="call-type-cards">
              {/* Discovery */}
              <Card
                className="border-emerald-200/60 hover:border-emerald-400 hover:shadow-lg transition-all cursor-pointer group"
                onClick={() => selectCallType('decouverte')}
                data-testid="call-type-decouverte"
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center">
                      <Gift className="w-5 h-5 text-emerald-600" />
                    </div>
                    <Badge variant="outline" className="text-[10px] border-emerald-200 text-emerald-700 bg-emerald-50">
                      1 seul par personne
                    </Badge>
                  </div>
                  <CardTitle className="text-base">Appel Découverte</CardTitle>
                  <CardDescription className="text-xs">Premier contact — orientation rapide</CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="flex items-baseline gap-2 mb-3">
                    <span className="text-2xl font-bold text-emerald-600">Gratuit</span>
                    <span className="text-sm text-muted-foreground">· 10 min</span>
                  </div>
                  <p className="text-xs text-muted-foreground mb-4">
                    {CALL_INFO.decouverte.description}
                  </p>
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground/70 mb-3">
                    <Clock className="w-3 h-3" /> Créneaux : 09h00 — 09h15
                  </div>
                  <Button variant="outline" size="sm" className="w-full rounded-lg gap-2 group-hover:bg-emerald-50 group-hover:border-emerald-300 group-hover:text-emerald-700 transition-colors" data-testid="select-decouverte">
                    Réserver <ArrowRight className="w-3.5 h-3.5" />
                  </Button>
                </CardContent>
              </Card>

              {/* Conseil */}
              <Card
                className="border-accent/30 hover:border-accent hover:shadow-lg transition-all cursor-pointer group ring-1 ring-accent/10"
                onClick={() => selectCallType('conseil')}
                data-testid="call-type-conseil"
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="w-10 h-10 rounded-xl bg-accent/10 flex items-center justify-center">
                      <Phone className="w-5 h-5 text-accent" />
                    </div>
                    <Badge variant="outline" className="text-[10px] border-accent/30 text-accent bg-accent/5">
                      Paiement requis
                    </Badge>
                  </div>
                  <CardTitle className="text-base">Appel Conseil</CardTitle>
                  <CardDescription className="text-xs">Échange structuré sur rendez-vous</CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="flex items-baseline gap-2 mb-3">
                    <span className="text-2xl font-bold text-accent">75 €</span>
                    <span className="text-sm text-muted-foreground">· 30 min</span>
                  </div>
                  <p className="text-xs text-muted-foreground mb-4">
                    {CALL_INFO.conseil.description}
                  </p>
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground/70 mb-3">
                    <Clock className="w-3 h-3" /> Créneaux : 14h00 — 16h30
                  </div>
                  <Button size="sm" className="w-full rounded-lg gap-2 transition-colors" data-testid="select-conseil">
                    <CreditCard className="w-3.5 h-3.5" /> Réserver & Payer <ArrowRight className="w-3.5 h-3.5" />
                  </Button>
                </CardContent>
              </Card>

              {/* Urgence */}
              <Card
                className="border-orange-200/60 hover:border-orange-400 hover:shadow-lg transition-all cursor-pointer group"
                onClick={() => selectCallType('urgence')}
                data-testid="call-type-urgence"
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="w-10 h-10 rounded-xl bg-orange-100 flex items-center justify-center">
                      <Zap className="w-5 h-5 text-orange-600" />
                    </div>
                    <Badge variant="outline" className="text-[10px] border-orange-200 text-orange-700 bg-orange-50">
                      Prioritaire
                    </Badge>
                  </div>
                  <CardTitle className="text-base">Appel Urgence</CardTitle>
                  <CardDescription className="text-xs">Réponse prioritaire rapide</CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="flex items-baseline gap-2 mb-3">
                    <span className="text-2xl font-bold text-orange-600">Dès 50 €</span>
                    <span className="text-sm text-muted-foreground">· sous 2h</span>
                  </div>
                  <p className="text-xs text-muted-foreground mb-4">
                    {CALL_INFO.urgence.description}
                  </p>
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground/70 mb-3">
                    <Shield className="w-3 h-3" /> Réponse garantie sous 2h ou 30 min
                  </div>
                  <Button variant="outline" size="sm" className="w-full rounded-lg gap-2 group-hover:bg-orange-50 group-hover:border-orange-300 group-hover:text-orange-700 transition-colors" data-testid="select-urgence">
                    <Zap className="w-3.5 h-3.5" /> Demande urgente
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>
      )}

      {/* Step 2: Calendar + Form */}
      {step === 'calendar' && callType && (
        <section className="section-padding">
          <div className="max-w-5xl mx-auto">
            {/* Back button + type info */}
            <div className="mb-6">
              <Button variant="ghost" size="sm" onClick={() => { setStep('choose'); setCallType(null); }} className="gap-1.5 text-muted-foreground mb-3" data-testid="back-to-types">
                <ArrowLeft className="w-3.5 h-3.5" /> Changer de format
              </Button>
              <div className="flex items-center gap-3">
                <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${callType === 'decouverte' ? 'bg-emerald-100' : 'bg-accent/10'}`}>
                  {callType === 'decouverte' ? <Gift className="w-4.5 h-4.5 text-emerald-600" /> : <Phone className="w-4.5 h-4.5 text-accent" />}
                </div>
                <div>
                  <h2 className="text-lg font-semibold">{CALL_INFO[callType].title}</h2>
                  <p className="text-xs text-muted-foreground">{CALL_INFO[callType].duration} — {CALL_INFO[callType].priceLabel}</p>
                </div>
              </div>
            </div>

            <div className="grid lg:grid-cols-2 gap-8">
              {/* Calendar */}
              <div>
                <Card className="border-border" data-testid="booking-calendar">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">
                        {MONTHS_FR[currentMonth.getMonth()]} {currentMonth.getFullYear()}
                      </CardTitle>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="icon" onClick={prevMonth}><ChevronLeft className="w-4 h-4" /></Button>
                        <Button variant="ghost" size="icon" onClick={nextMonth}><ChevronRight className="w-4 h-4" /></Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-7 gap-1 mb-2">
                      {DAYS_FR.map(d => <div key={d} className="text-center text-xs font-medium text-muted-foreground py-2">{d}</div>)}
                    </div>
                    <div className="grid grid-cols-7 gap-1">
                      {getDaysInMonth(currentMonth).map((day, i) => (
                        <button
                          key={i}
                          disabled={!day || isWeekend(day) || isPast(day)}
                          onClick={() => day && handleDateClick(day)}
                          className={`aspect-square rounded-lg text-sm font-medium transition-all
                            ${!day ? 'invisible' : ''}
                            ${day && isSameDay(day, selectedDate) ? 'bg-accent text-accent-foreground shadow-md' : ''}
                            ${day && isToday(day) && !isSameDay(day, selectedDate) ? 'bg-muted font-bold' : ''}
                            ${day && !isWeekend(day) && !isPast(day) && !isSameDay(day, selectedDate) ? 'hover:bg-muted cursor-pointer' : ''}
                            ${day && (isWeekend(day) || isPast(day)) ? 'text-muted-foreground/30 cursor-not-allowed' : ''}
                          `}
                          data-testid={day ? `cal-day-${day.getDate()}` : undefined}
                        >
                          {day?.getDate()}
                        </button>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Time Slots */}
                {selectedDate && (
                  <Card className="border-border mt-4" data-testid="time-slots">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm flex items-center gap-2">
                        <Clock className="w-4 h-4 text-accent" />
                        {selectedDate.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {loadingSlots ? (
                        <div className="flex justify-center py-4"><Loader2 className="w-6 h-6 animate-spin text-muted-foreground" /></div>
                      ) : availableSlots.length === 0 ? (
                        <p className="text-sm text-muted-foreground text-center py-4">Aucun créneau disponible ce jour.</p>
                      ) : (
                        <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                          {availableSlots.map(slot => (
                            <button
                              key={slot}
                              onClick={() => setSelectedSlot(slot)}
                              className={`py-2 px-3 rounded-lg text-sm font-medium border transition-all
                                ${selectedSlot === slot
                                  ? 'bg-accent text-accent-foreground border-accent shadow-md'
                                  : 'border-border hover:border-accent/50 hover:bg-muted'
                                }
                              `}
                              data-testid={`slot-${slot.replace(':', '')}`}
                            >
                              {slot}
                            </button>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}
              </div>

              {/* Form */}
              <div>
                <Card className="border-border" data-testid="booking-form">
                  <CardHeader>
                    <CardTitle className="text-base">Vos informations</CardTitle>
                    <CardDescription className="text-xs">
                      {callType === 'decouverte'
                        ? 'Remplissez le formulaire pour confirmer votre rendez-vous gratuit.'
                        : 'Remplissez le formulaire. Vous serez redirigé vers le paiement sécurisé.'}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handleSubmit} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="book-name">Nom complet *</Label>
                        <Input id="book-name" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} placeholder="Prénom Nom" required data-testid="book-name" />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="book-email">Email *</Label>
                        <Input id="book-email" type="email" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} placeholder="votre@email.fr" required data-testid="book-email" />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="book-phone">Téléphone</Label>
                        <Input id="book-phone" value={form.phone} onChange={e => setForm(f => ({ ...f, phone: e.target.value }))} placeholder="06 00 00 00 00" data-testid="book-phone" />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="book-message">Message (optionnel)</Label>
                        <Textarea id="book-message" value={form.message} onChange={e => setForm(f => ({ ...f, message: e.target.value }))} placeholder="Décrivez brièvement votre situation..." rows={3} data-testid="book-message" />
                      </div>

                      {/* Summary */}
                      {selectedDate && selectedSlot && (
                        <div className="bg-muted/50 p-4 rounded-xl" data-testid="booking-summary">
                          <p className="text-sm font-medium mb-1">Récapitulatif</p>
                          <p className="text-sm text-muted-foreground">
                            {CALL_INFO[callType].title} le{' '}
                            <strong>{selectedDate.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })}</strong> à <strong>{selectedSlot}</strong>
                          </p>
                          {callType === 'conseil' && (
                            <p className="text-sm font-medium text-accent mt-1">
                              <CreditCard className="w-3.5 h-3.5 inline mr-1" />
                              Montant : 75 €
                            </p>
                          )}
                        </div>
                      )}

                      {callType !== 'decouverte' && (
                        <div className="flex items-start gap-2">
                          <input
                            type="checkbox"
                            id="cgv-booking"
                            checked={cgvAccepted}
                            onChange={(e) => setCgvAccepted(e.target.checked)}
                            className="mt-0.5 rounded border-gray-300 text-accent focus:ring-accent"
                            data-testid="cgv-consent-checkbox-booking"
                          />
                          <label htmlFor="cgv-booking" className="text-[10px] text-muted-foreground leading-relaxed cursor-pointer">
                            J'accepte les{' '}
                            <a href="/mentions-legales?tab=cgv" target="_blank" rel="noopener" className="text-accent underline">
                              CGV
                            </a>{' '}
                            et renonce à mon droit de rétractation (art. L.221-28 C. conso.), la prestation étant exécutée immédiatement après paiement.
                          </label>
                        </div>
                      )}

                      <Button
                        type="submit"
                        className="w-full rounded-lg gap-2"
                        disabled={submitting || !selectedDate || !selectedSlot || (callType !== 'decouverte' && !cgvAccepted)}
                        data-testid="confirm-booking-button"
                      >
                        {submitting ? (
                          <><Loader2 className="w-4 h-4 animate-spin" />Traitement...</>
                        ) : callType === 'decouverte' ? (
                          <><CalendarIcon className="w-4 h-4" />Confirmer le rendez-vous</>
                        ) : (
                          <><CreditCard className="w-4 h-4" />Payer et réserver — 75 €</>
                        )}
                      </Button>

                      <p className="text-xs text-muted-foreground text-center">
                        {callType === 'decouverte'
                          ? CALL_INFO.decouverte.note
                          : <>Paiement sécurisé par Stripe. Le créneau est confirmé uniquement après paiement.</>
                        }
                      </p>
                    </form>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </section>
      )}
    </main>
  );
};

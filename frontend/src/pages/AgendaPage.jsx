import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { 
  Calendar as CalendarIcon, 
  Clock, 
  Phone, 
  Video, 
  CheckCircle, 
  ArrowRight, 
  Loader2,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import axios from 'axios';
import { SEO } from '@/components/SEO';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const DAYS_FR = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'];
const MONTHS_FR = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];

export const AgendaPage = () => {
  const [selectedDate, setSelectedDate] = useState(null);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [booked, setBooked] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [form, setForm] = useState({ name: '', email: '', phone: '', booking_type: 'téléphone', message: '' });

  const formatDateStr = (date) => {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  };

  const fetchSlots = async (dateStr) => {
    setLoadingSlots(true);
    try {
      const res = await axios.get(`${API}/bookings/slots/${dateStr}`);
      setAvailableSlots(res.data.slots);
    } catch { setAvailableSlots([]); }
    finally { setLoadingSlots(false); }
  };

  const handleDateClick = (date) => {
    setSelectedDate(date);
    setSelectedSlot(null);
    fetchSlots(formatDateStr(date));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedDate || !selectedSlot || !form.name || !form.email) {
      toast.error("Veuillez remplir tous les champs obligatoires");
      return;
    }
    setSubmitting(true);
    try {
      await axios.post(`${API}/bookings`, {
        ...form,
        date: formatDateStr(selectedDate),
        time_slot: selectedSlot
      });
      setBooked(true);
      toast.success("Rendez-vous confirmé !");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur lors de la réservation");
    } finally { setSubmitting(false); }
  };

  // Calendar generation
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

  if (booked) {
    return (
      <main className="page-transition pt-20 min-h-screen flex items-center">
      <SEO title="Prendre rendez-vous" description="Réservez un créneau pour un échange gratuit avec notre expert en maladie professionnelle et droits sociaux." path="/agenda" />
        <div className="max-w-2xl mx-auto px-4 text-center py-20">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10 text-green-600" strokeWidth={1.5} />
          </div>
          <h2 className="text-3xl font-semibold mb-4" data-testid="booking-success-title">Rendez-vous confirmé !</h2>
          <p className="text-muted-foreground mb-2">
            <strong>{form.booking_type === 'téléphone' ? 'Appel téléphonique' : 'Visioconférence'}</strong>
          </p>
          <p className="text-muted-foreground mb-6">
            Le <strong>{selectedDate?.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })}</strong> à <strong>{selectedSlot}</strong>
          </p>
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
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Agenda</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="agenda-title">
              Prendre rendez-vous
            </h1>
            <p className="text-lg text-muted-foreground">
              Réservez un créneau pour une première consultation téléphonique gratuite — 10 minutes pour évaluer votre situation.
              Choisissez la date et l'heure qui vous conviennent.
            </p>
          </div>
        </div>
      </section>

      <section className="section-padding">
        <div className="max-w-5xl mx-auto">
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
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <Clock className="w-4 h-4 text-accent" />
                      Créneaux du {selectedDate.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })}
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

            {/* Booking Form */}
            <div>
              <Card className="border-border" data-testid="booking-form">
                <CardHeader>
                  <CardTitle>Vos informations</CardTitle>
                  <CardDescription>Remplissez le formulaire pour confirmer votre rendez-vous.</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-2">
                      <Label>Type de rendez-vous *</Label>
                      <div className="grid grid-cols-2 gap-3">
                        <button type="button"
                          onClick={() => setForm(f => ({ ...f, booking_type: 'téléphone' }))}
                          className={`flex items-center gap-2 p-3 rounded-lg border text-sm font-medium transition-all
                            ${form.booking_type === 'téléphone' ? 'border-accent bg-accent/10 text-accent' : 'border-border hover:border-accent/50'}`}
                          data-testid="type-téléphone"
                        >
                          <Phone className="w-4 h-4" /> Téléphone
                        </button>
                        <button type="button"
                          onClick={() => setForm(f => ({ ...f, booking_type: 'visio' }))}
                          className={`flex items-center gap-2 p-3 rounded-lg border text-sm font-medium transition-all
                            ${form.booking_type === 'visio' ? 'border-accent bg-accent/10 text-accent' : 'border-border hover:border-accent/50'}`}
                          data-testid="type-visio"
                        >
                          <Video className="w-4 h-4" /> Visioconférence
                        </button>
                      </div>
                    </div>
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

                    {selectedDate && selectedSlot && (
                      <div className="bg-muted/50 p-4 rounded-xl" data-testid="booking-summary">
                        <p className="text-sm font-medium mb-1">Récapitulatif</p>
                        <p className="text-sm text-muted-foreground">
                          {form.booking_type === 'téléphone' ? 'Appel téléphonique' : 'Visioconférence'} le{' '}
                          <strong>{selectedDate.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })}</strong> à <strong>{selectedSlot}</strong>
                        </p>
                      </div>
                    )}

                    <Button type="submit" className="w-full rounded-lg gap-2" disabled={submitting || !selectedDate || !selectedSlot} data-testid="confirm-booking-button">
                      {submitting ? <><Loader2 className="w-4 h-4 animate-spin" />Confirmation...</> : <><CalendarIcon className="w-4 h-4" />Confirmer le rendez-vous</>}
                    </Button>
                    <p className="text-xs text-muted-foreground text-center">Première consultation gratuite — 10 minutes, sans engagement.</p>
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

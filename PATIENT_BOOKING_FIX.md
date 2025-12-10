# Final Patient Appointment Booking Fix

## Update PatientFindDoctors.tsx - Doctor Card Rendering

Replace the doctor card rendering section (lines ~101-167) with:

```tsx
{filteredDoctors.map((doctor) => (
  <Card key={doctor.id} className="hover:shadow-lg transition-shadow">
    <CardHeader>
      <div className="flex items-start gap-4">
        <Avatar className="h-16 w-16">
          <AvatarFallback className="bg-primary text-primary-foreground text-xl">
            {doctor.full_name?.split(' ').map(n => n[0]).join('') || 'D'}
          </AvatarFallback>
        </Avatar>
        <div className="flex-1 min-w-0">
          <CardTitle className="text-lg mb-1">
            Dr. {doctor.full_name || 'Doctor'}
          </CardTitle>
          <Badge variant="outline" className="mb-2">
            {doctor.specialization_name || 'Specialist'}
          </Badge>
          {doctor.rating && (
            <div className="flex items-center gap-1">
              <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
              <span className="text-sm font-medium">{doctor.rating.toFixed(1)}</span>
              <span className="text-xs text-muted-foreground ml-1">rating</span>
            </div>
          )}
        </div>
      </div>
    </CardHeader>
    <CardContent className="space-y-4">
      {/* Experience */}
      <div className="flex items-center gap-2 text-sm">
        <Stethoscope className="h-4 w-4 text-muted-foreground" />
        <span>{doctor.experience_years} years experience</span>
      </div>

      {/* Bio */}
      {doctor.bio && (
        <div>
          <p className="text-sm font-medium mb-1">About</p>
          <p className="text-sm text-muted-foreground line-clamp-3">{doctor.bio}</p>
        </div>
      )}

      {/* License */}
      <div className="pt-3 border-t">
        <p className="text-xs text-muted-foreground">
          License: {doctor.license_number}
        </p>
      </div>

      {/* Actions */}
      <div className="flex gap-2 pt-2">
        <Button
          className="flex-1"
          onClick={() => handleBookAppointment(doctor)}
          disabled={doctor.status !== 'approved'}
        >
          <Calendar className="mr-2 h-4 w-4" />
          Book Appointment
        </Button>
        <Button variant="outline" size="icon">
          <Search className="h-4 w-4" />
        </Button>
      </div>
    </CardContent>
  </Card>
))}
```

## Add Booking Dialog at the End (before closing div)

Add this before the final `</div>`:

```tsx
{/* Booking Dialog */}
<Dialog open={bookingDialogOpen} onOpenChange={setBookingDialogOpen}>
  <DialogContent className="sm:max-w-[500px]">
    <DialogHeader>
      <DialogTitle>Book Appointment</DialogTitle>
    </DialogHeader>
    {selectedDoctor && (
      <div className="space-y-4">
        <div className="flex items-center gap-3 p-4 rounded-lg bg-muted">
          <Avatar className="h-12 w-12">
            <AvatarFallback className="bg-primary text-primary-foreground">
              {selectedDoctor.full_name?.split(' ').map(n => n[0]).join('') || 'D'}
            </AvatarFallback>
          </Avatar>
          <div>
            <p className="font-semibold">Dr. {selectedDoctor.full_name}</p>
            <p className="text-sm text-muted-foreground">{selectedDoctor.specialization_name}</p>
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="datetime">Appointment Date & Time *</Label>
          <Input
            id="datetime"
            type="datetime-local"
            value={bookingDateTime}
            onChange={(e) => setBookingDateTime(e.target.value)}
            min={new Date().toISOString().slice(0, 16)}
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="notes">Notes (Optional)</Label>
          <Textarea
            id="notes"
            placeholder="Any specific concerns or symptoms..."
            value={bookingNotes}
            onChange={(e) => setBookingNotes(e.target.value)}
            rows={3}
          />
        </div>

        <div className="flex gap-2 pt-4">
          <Button
            variant="outline"
            className="flex-1"
            onClick={() => setBookingDialogOpen(false)}
            disabled={bookingMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            className="flex-1"
            onClick={handleSubmitBooking}
            disabled={bookingMutation.isPending || !bookingDateTime}
          >
            {bookingMutation.isPending ? 'Booking...' : 'Confirm Booking'}
          </Button>
        </div>
      </div>
    )}
  </DialogContent>
</Dialog>
```

## Update Specialization Filter

Replace line ~71-75 with:

```tsx
{specializations.map((spec) => (
  <option key={spec.id} value={spec.title}>
    {spec.title}
  </option>
))}
```

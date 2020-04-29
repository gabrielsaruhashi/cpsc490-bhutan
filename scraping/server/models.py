from app import db

class GPSTrip(db.Model):
    __tablename__ = 'gps'

    id = db.Column(db.Integer, primary_key=True)
    TripStartAddress = db.Column(db.String())
    TripStopAddress = db.Column(db.String())
    LatLngStart = db.Column(db.String())
    LatLngEnd = db.Column(db.String())
    Dzongkha = db.Column(db.String())
    AmbulanceNo = db.Column(db.String())
    StartTime = db.Column(db.String())
    EndTime = db.Column(db.String())
    TripDuration = db.Column(db.String())
    DistanceTravelled = db.Column(db.String())

    def __init__(self, TripStartAddress, TripStopAddress, LatLngStart, LatLngEnd, Dzongkha, 
        AmbulanceNo, StartTime, EndTime, TripDuration, DistanceTravelled):
        self.TripStartAddress = TripStartAddress
        self.TripStopAddress = TripStopAddress
        self.LatLngStart = LatLngStart
        self.LatLngEnd = LatLngEnd
        self.Dzongkha = Dzongkha
        self.AmbulanceNo = AmbulanceNo
        self.StartTime = StartTime
        self.EndTime = EndTime
        self.TripDuration = TripDuration
        self.DistanceTravelled = DistanceTravelled

    def __repr__(self):
        return '<id {}>'.format(self.id)
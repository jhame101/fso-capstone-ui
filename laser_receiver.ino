//Libraries


//Constants
#define PHOTO_PIN A0
#define MAX_VOLTAGE 5

void setup()
{
    Serial.begin(57600);

    initializeReceiver();
}

void loop()
{

    currentTime = millis()
    int analogue_value = analogRead(PHOTO_PIN);

    float voltage = analogue_value*MAX_VOLTAGE/1024.f;

    // Serial.println(sprintf(
    // "Time: %f, Humidity: %f%%, Temp:%fC, Pressure: %fPa, Light: %flx, (Roll: %f, Pitch: %f, Yaw: %f) deg",   // no \n since println adds one
    // currentTime,    hum,       temp,     pa,             lux,           roll,    pitch,     yaw
    // ))

}

int initializeReceiver() {
    pinMode(A0, INPUT);

    return 0;
}
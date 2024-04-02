// Libraries


// Constants
#define PHOTO_PIN A0
/*
- 
*/

// global variables


void setup()
{
    Serial.begin(57600);

    Serial.println(sprintf("Size of int: %d",sizeof(int)));
    Serial.println("If int isn't 2 bytes, transmission will fail.");

    initializeReceiver();
}

void loop()
{
    // wait for confirmation from pi
    for (c=0; c<1000; c++) {

    }
    // Serial.println(sprintf(
    // "Time: %f, Humidity: %f%%, Temp:%fC, Pressure: %fPa, Light: %flx, (Roll: %f, Pitch: %f, Yaw: %f) deg",   // no \n since println adds one
    // currentTime,    hum,       temp,     pa,             lux,           roll,    pitch,     yaw
    // ))

}

int initializeReceiver() {
    pinMode(PHOTO_PIN, INPUT);

    return 0;
}

// WARNING: the following function works on Arduino Uno because ints are specifically 16 bits
// If running on different hardware, the number of bits sent may need to change
void sendOnePDReading() {
    // reads one value from the photodiode and then sends it over serial, along with the time it was taken

    static unsigned long previous_time;
    
    // Define struct for sending data
    struct {
        unsigned int elapsed_time;
        unsigned int analogue_value;
    } pdReading;
    unsigned long current_time;

    // take reading
    pdReading.analogue_value = analogRead(PHOTO_PIN);
    current_time = micros()/100;    // Record current time in units of 1e-4 seconds

    pdReading.elapsed_time = (unsigned int) (current_time - previous_time); // explicitly cast result of long subtraction to int

    previous_time = current_time;   // reset current time for the next round

    // send data over the serial connection
    Serial.write((byte*) &pdReading, 4);    // sending 2 ints -> 4 bytes
}
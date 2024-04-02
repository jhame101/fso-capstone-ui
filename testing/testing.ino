void setup() {
  Serial.begin(57600);

}

void loop() {
  static unsigned int a = 0;
  static unsigned int b = 1;

  sendOnePoint(a,b);

  a = b+a;
  swapints(&a, &b);

  delay(500);
}

void swapints(unsigned int* x, unsigned int* y) {
  int z = *x;
  *x = *y;
  *y = z;
}

void sendOnePoint(int x, int y) {
    // Define struct for sending data
    struct {
        unsigned int a;
        unsigned int b;
    } pdReading;

    // Fill struct
    pdReading.a = x;
    pdReading.b = y;

    // send data over the serial connection
    Serial.write((byte*) &pdReading, 4);    // sending 2 ints -> 4 bytes
}

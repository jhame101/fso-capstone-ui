//Libraries
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_BMP280.h>
#include <BH1750.h>
#include <i2cdetect.h>

//Constants
#define DHTPIN 3     // what pin we're connected to with the temp/hum sensor
#define DHTTYPE DHT22   // DHT 22  (AM2302)
#define seaLevelPressure_hPa 1013.25
#define BMP085_I2CADDR 0x77
#define BMP280_ADDRESS 0x76

#define PHOTO_PIN A0

DHT dht(DHTPIN, DHTTYPE); //// Initialize DHT sensor for normal 16mhz Arduino 
// Adafruit_BMP085 bmp; 
Adafruit_BMP280 bmp; // I2C
BH1750 lightMeter(0x23);

//Variables 
int chk;
const int MPU = 0x68; // MPU6050 I2C address
float AccX, AccY, AccZ;
float GyroX, GyroY, GyroZ;
float accAngleX, accAngleY, gyroAngleX, gyroAngleY, gyroAngleZ;
float roll, pitch, yaw;
float AccErrorX, AccErrorY, GyroErrorX, GyroErrorY, GyroErrorZ;
float elapsedTime, currentTime, previousTime;

// Function prototypes
void I2Cdetector();
void DHTsetup();
void MPUsetup();
void BMP280setup();
void BH1750setup();
void calculate_IMU_error();
void readGyro();
void sendOnePDReading();

void setup() 
{ 
  Serial.begin(57600); 
  while (!Serial);   // wait for serial monitor
  Wire.begin(); 
  
  I2Cdetector();
  DHTsetup();
  BMP280setup();
  BH1750setup();
  MPUsetup();

  pinMode(PHOTO_PIN, INPUT);
}

void loop()
{
  // wait for confirmation from UI

  for (int c = 0; c < 1000; c++) {
    sendOnePDReading();   // Send one 4 byte reading over serial
  }

  //Read data and store it to variables hum, temp, pa, alt 
  float hum = dht.readHumidity(); 
  float temp= dht.readTemperature(); //Stores temperature value
  float pa = bmp.readPressure(); 
  float alt = bmp.readAltitude(); 
  float temp2 = bmp.readTemperature(); // stores bmp temp
  float lux = lightMeter.readLightLevel(); // store light value
  readGyro();
  
  Serial.print("Time: ");
  Serial.print(currentTime);
  Serial.print(", Humidity: ");
  Serial.print(hum);
  Serial.print("%, Temp:");
  Serial.print(temp);
  Serial.print("C, Pressure: ");
  Serial.print(pa);
  Serial.print("Pa, Altitude: ");
  Serial.print(alt);
  Serial.print("m, Temp (BMP): ");
  Serial.print(temp2);
  Serial.print("C, Light: ");
  Serial.print(lux);
  Serial.print("lx, (Roll: ");
  Serial.print(roll);
  Serial.print(", Pitch: ");
  Serial.print(pitch);
  Serial.print(", Yaw: ");
  Serial.print(yaw);
  Serial.println(") deg");

  delay(1000); //Delay 1 sec. 
} 

void I2Cdetector()
{
  Serial.println("\nI2C Scanner");
  byte error, address;
  int nDevices;
 
  Serial.println("Scanning...");
 
  nDevices = 0;
  for(address = 1; address < 127; address++ )
  {
    // The i2c_scanner uses the return value of
    // the Write.endTransmisstion to see if
    // a device did acknowledge to the address.
    Wire.beginTransmission(address);
    error = Wire.endTransmission();
 
    if (error == 0)
    {
      Serial.print("I2C device found at address 0x");
      if (address<16)
        Serial.print("0");
      Serial.print(address,HEX);
      Serial.println("  !");
 
      nDevices++;
    }
    else if (error==4)
    {
      Serial.print("Unknown error at address 0x");
      if (address<16)
        Serial.print("0");
      Serial.println(address,HEX);
    }    
  }
  if (nDevices == 0)
    Serial.println("No I2C devices found\n");
  else
    Serial.println("done\n");
}
void DHTsetup()
{
  dht.begin();
}

void MPUsetup()
{
  Wire.beginTransmission(MPU);// Start communication with MPU6050 (MPU=0x68) 
  Wire.write(0x6B);// Talk to the register 6B 
  Wire.write(0x00);// Make reset - place a 0 into the 6B register 
  Wire.endTransmission(true);//end the transmission

  // Configure Accelerometer Sensitivity - Full Scale Range (default +/- 2g) 
  Wire.beginTransmission(MPU); 
  Wire.write(0x1C);//Talk to the ACCEL_CONFIG register (1C hex) 
  Wire.write(0x10);//Set the register bits as 00010000 (+/- 8g full scale range) 
  Wire.endTransmission(true); 

  // Configure Gyro Sensitivity - Full Scale Range (default +/- 250deg/s) 
  Wire.beginTransmission(MPU); 
  Wire.write(0x1B);// Talk to the GYRO_CONFIG register (1B hex) 
  Wire.write(0x10);// Set the register bits as 00010000 (1000deg/s full scale) 
  Wire.endTransmission(true); 
  delay(20); 

  // Call this function if you need to get the IMU error values for your module 
  calculate_IMU_error();
  delay(20);
}

void BMP280setup()
{
  while ( !Serial ) delay(100);   // wait for native usb
  Serial.println(F("BMP280 test"));
  bmp.begin(BMP280_ADDRESS);
  if (bmp.begin(BMP280_ADDRESS)) { 
    Serial.println(F("BMP280 initialised")); 
  } 
  else { 
   Serial.println(F("Error initialising BMP280")); 
  } 
  Serial.println(F("BPM280 Test begin")); 

}
void BH1750setup()
{
  lightMeter.begin(); 
  if (lightMeter.begin()) { 
    Serial.println(F("BH1750 initialised")); 
  } 
  else { 
   Serial.println(F("Error initialising BH1750")); 
  } 
  Serial.println(F("BH1750 Test begin")); 
}

void calculate_IMU_error() { 

  // We can call this funtion in the setup section to calculate the accelerometer and gyro data error. From here we will get the error values used in the above equations printed on the Serial Monitor. 
  // Note that we should place the IMU flat in order to get the proper values, so that we then can the correct values 
  // Read accelerometer values 200 times 

  for(int c=0; c < 200; c++) { 
    Wire.beginTransmission(MPU); 

    Wire.write(0x3B); 

    Wire.endTransmission(false); 

    Wire.requestFrom(MPU, 6, true);

    AccX = (Wire.read() << 8 | Wire.read()) / 16384.0 ;
    AccY = (Wire.read() << 8 | Wire.read()) / 16384.0 ;
    AccZ = (Wire.read() << 8 | Wire.read()) / 16384.0 ;

    // Sum all readings 
    AccErrorX = AccErrorX + ((atan((AccY) / sqrt(pow((AccX), 2) + pow((AccZ), 2))) * 180 / PI));
    AccErrorY = AccErrorY + ((atan(-1 * (AccX) / sqrt(pow((AccY), 2) + pow((AccZ), 2))) * 180 / PI));
  } 

  //Divide the sum by 200 to get the error value 

  AccErrorX = AccErrorX / 200; 
  AccErrorY = AccErrorY / 200; 

  // Read gyro values 200 times
  for (int c=0; c < 200; c++) { 
    Wire.beginTransmission(MPU); 

    Wire.write(0x43); 

    Wire.endTransmission(false); 

    Wire.requestFrom(MPU, 6, true);

    GyroX = Wire.read() << 8 | Wire.read();
    GyroY = Wire.read() << 8 | Wire.read();
    GyroZ = Wire.read() << 8 | Wire.read();

    // Sum all readings 

    GyroErrorX = GyroErrorX + (GyroX / 131.0);
    GyroErrorY = GyroErrorY + (GyroY / 131.0);
    GyroErrorZ = GyroErrorZ + (GyroZ / 131.0);
  } 

  //Divide the sum by 200 to get the error value 

  GyroErrorX = GyroErrorX / 200;
  GyroErrorY = GyroErrorY / 200;
  GyroErrorZ = GyroErrorZ / 200;

  // Print the error values on the Serial Monitor 
  // Serial.print("AccErrorX: ");
  // Serial.println(AccErrorX);
  // Serial.print("AccErrorY: ");
  // Serial.println(AccErrorY);
  // Serial.print("GyroErrorX: ");
  // Serial.println(GyroErrorX);
  // Serial.print("GyroErrorY: ");
  // Serial.println(GyroErrorY);
  // Serial.print("GyroErrorZ: ");
  // Serial.println(GyroErrorZ);
} 

void readGyro()
{
  // === Read acceleromter data === //
  Wire.beginTransmission(MPU); 
  Wire.write(0x3B); // Start with register 0x3B (ACCEL_XOUT_H) 
  Wire.endTransmission(false); 
  Wire.requestFrom(MPU, 6, true); // Read 6 registers total, each axis value is stored in 2 registers 

    //For a range of +-2g, we need to divide the raw values by 16384, according to the datasheet 
  AccX = (Wire.read() << 8 | Wire.read()) / 16384.0; // X-axis value 
  AccY = (Wire.read() << 8 | Wire.read()) / 16384.0; // Y-axis value 
  AccZ = (Wire.read() << 8 | Wire.read()) / 16384.0; // Z-axis value 

    // Calculating Roll and Pitch from the accelerometer data 
  accAngleX = (atan(AccY / sqrt(pow(AccX, 2) + pow(AccZ, 2))) * 180 / PI) - AccErrorX; // AccErrorX ~(0.58) See the calculate_IMU_error()custom function for more details 
  accAngleY = (atan(-1 * AccX / sqrt(pow(AccY, 2) + pow(AccZ, 2))) * 180 / PI) - AccErrorY; // AccErrorY ~(-1.58)

  // === Read gyroscope data === // 
  previousTime = currentTime;// Previous time is stored before the actual time read 
  currentTime = millis();// Current time actual time read 
  elapsedTime = (currentTime - previousTime) / 1000;// Divide by 1000 to get seconds 
  
  Wire.beginTransmission(MPU); 
  Wire.write(0x43);// Gyro data first register address 0x43 
  Wire.endTransmission(false); 
  Wire.requestFrom(MPU, 6, true);// Read 4 registers total, each axis value is stored in 2 registers 
  
  GyroX = (Wire.read() << 8 | Wire.read()) / 131.0;// For a 250deg/s range we have to divide first the raw value by 131.0, according to the datasheet 
  GyroY = (Wire.read() << 8 | Wire.read()) / 131.0; 
  GyroZ = (Wire.read() << 8 | Wire.read()) / 131.0; 

  // Correct the outputs with the calculated error values 
  GyroX = GyroX - GyroErrorX; // GyroErrorX ~(-0.56) 
  GyroY = GyroY - GyroErrorY; // GyroErrorY ~(2) 
  GyroZ = GyroZ - GyroErrorZ; // GyroErrorZ ~ (-0.8) 

  // Currently the raw values are in degrees per seconds, deg/s, so we need to multiply by sendonds (s) to get the angle in degrees 
  gyroAngleX = gyroAngleX + GyroX * elapsedTime; // deg/s * s = deg 
  gyroAngleY = gyroAngleY + GyroY * elapsedTime; 
  yaw =  yaw + GyroZ * elapsedTime; 

  // Complementary filter - combine acceleromter and gyro angle values 
  roll = 0.96 * gyroAngleX + 0.04 * accAngleX; 
  pitch = 0.96 * gyroAngleY + 0.04 * accAngleY; 
}

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

#include "esphome.h"
#include "Adafruit_SHT31.h"

// Requires this lib installed: $ platformio lib --global install "Adafruit BusIO"

class SHT31CustomSensor : public PollingComponent, public Sensor {
public:
  Adafruit_SHT31 sht31 = Adafruit_SHT31();

  Sensor *temperature_sensor = new Sensor();
  Sensor *humidity_sensor = new Sensor();

SHT31CustomSensor() : PollingComponent(15000) {}
void setup() override {
    Wire.begin();
    sht31.begin(0x44);
}

void update() override {
    float temperature= sht31.readTemperature();
    float humidity = sht31.readHumidity();
    ESP_LOGD("SHT31", "The value of sensor temperature is: %.1f", temperature);
    ESP_LOGD("SHT31", "The value of sensor humidity is: %.1f", humidity);
    temperature_sensor->publish_state(temperature);
    humidity_sensor->publish_state(humidity);
}

};

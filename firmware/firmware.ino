#include "esp_camera.h"

// ====== Select the XIAO ESP32S3 Sense pin map ======
#define CAMERA_MODEL_XIAO_ESP32S3
#include "camera_pins.h"

void setup() {
  Serial.begin(115200);
  delay(2000);

  // ---- camera config ----
  camera_config_t c;
  c.ledc_channel = LEDC_CHANNEL_0;
  c.ledc_timer   = LEDC_TIMER_0;
  c.pin_d0 = Y2_GPIO_NUM;  c.pin_d1 = Y3_GPIO_NUM;  c.pin_d2 = Y4_GPIO_NUM;  c.pin_d3 = Y5_GPIO_NUM;
  c.pin_d4 = Y6_GPIO_NUM;  c.pin_d5 = Y7_GPIO_NUM;  c.pin_d6 = Y8_GPIO_NUM;  c.pin_d7 = Y9_GPIO_NUM;
  c.pin_xclk = XCLK_GPIO_NUM; c.pin_pclk = PCLK_GPIO_NUM;
  c.pin_vsync = VSYNC_GPIO_NUM; c.pin_href = HREF_GPIO_NUM;
  c.pin_sscb_sda = SIOD_GPIO_NUM; c.pin_sscb_scl = SIOC_GPIO_NUM;
  c.pin_pwdn = PWDN_GPIO_NUM; c.pin_reset = RESET_GPIO_NUM;
  c.xclk_freq_hz = 20000000;
  c.pixel_format = PIXFORMAT_JPEG;
  c.frame_size   = FRAMESIZE_SVGA;   // 800x600 to start
  c.jpeg_quality = 12;
  c.fb_count     = 1;
  c.fb_location  = CAMERA_FB_IN_PSRAM;

  if (esp_camera_init(&c) != ESP_OK) {
    Serial.println("Camera init failed");
    while (true) delay(1000);
  }

  Serial.println("Ready. Send any key to capture.");
}

void loop() {
  if (Serial.available()) {
    Serial.read(); // clear one byte
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Capture failed");
      return;
    }

    // send start marker
    Serial.write(0xAA);
    Serial.write(0x55);

    // send length (4 bytes little endian)
    uint32_t len = fb->len;
    Serial.write((uint8_t*)&len, 4);

    // send JPEG bytes
    Serial.write(fb->buf, fb->len);

    esp_camera_fb_return(fb);
    Serial.println("Done");
  }
}




// WIFI VERSION
/*
  XIAO ESP32S3 Sense - WiFi photo-only firmware
  - Endpoint:  http://<ip>/capture  -> single JPEG
  - No UI, no MJPEG stream, no audio
  - In Arduino IDE: Tools -> PSRAM -> Enabled
  - Board: XIAO_ESP32S3
*/

// #include <WiFi.h>
// #include "esp_camera.h"
// #include "esp_http_server.h"

// // ====== Wi-Fi (fill these) ======
// const char* WIFI_SSID = "Related313";
// const char* WIFI_PASS = "Starry313";

// // ====== Camera pin map for XIAO ESP32S3 Sense ======
// #define CAMERA_MODEL_XIAO_ESP32S3  // important: select this before including camera_pins.h
// #include "camera_pins.h"

// // ====== Optional tuning ======
// static framesize_t FRAME_SIZE = FRAMESIZE_SVGA; // 800x600 is safe. Try FRAMESIZE_XGA/UXGA later
// static int JPEG_QUALITY = 12;                   // 0..63 (lower = better quality & larger file)

// httpd_handle_t httpd = NULL;

// static esp_err_t capture_handler(httpd_req_t *req) {
//   camera_fb_t *fb = esp_camera_fb_get();
//   if (!fb || fb->format != PIXFORMAT_JPEG) {
//     if (fb) esp_camera_fb_return(fb);
//     httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "Capture failed");
//     return ESP_FAIL;
//   }
//   httpd_resp_set_type(req, "image/jpeg");
//   httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg");
//   esp_err_t res = httpd_resp_send(req, (const char*)fb->buf, fb->len);
//   esp_camera_fb_return(fb);
//   return res;
// }

// static void start_server() {
//   httpd_config_t cfg = HTTPD_DEFAULT_CONFIG();
//   cfg.server_port = 80;
//   if (httpd_start(&httpd, &cfg) == ESP_OK) {
//     httpd_uri_t cap = { .uri="/capture", .method=HTTP_GET, .handler=capture_handler, .user_ctx=NULL };
//     httpd_register_uri_handler(httpd, &cap);
//   }
// }

// void setup() {
//   Serial.begin(115200);
//   delay(200);

//   // ---- Camera config ----
//   camera_config_t c = {};
//   c.ledc_channel = LEDC_CHANNEL_0;
//   c.ledc_timer   = LEDC_TIMER_0;
//   c.pin_d0 = Y2_GPIO_NUM;  c.pin_d1 = Y3_GPIO_NUM;  c.pin_d2 = Y4_GPIO_NUM;  c.pin_d3 = Y5_GPIO_NUM;
//   c.pin_d4 = Y6_GPIO_NUM;  c.pin_d5 = Y7_GPIO_NUM;  c.pin_d6 = Y8_GPIO_NUM;  c.pin_d7 = Y9_GPIO_NUM;
//   c.pin_xclk = XCLK_GPIO_NUM;
//   c.pin_pclk = PCLK_GPIO_NUM;
//   c.pin_vsync = VSYNC_GPIO_NUM;
//   c.pin_href = HREF_GPIO_NUM;
//   c.pin_sscb_sda = SIOD_GPIO_NUM;
//   c.pin_sscb_scl = SIOC_GPIO_NUM;
//   c.pin_pwdn = PWDN_GPIO_NUM;
//   c.pin_reset = RESET_GPIO_NUM;
//   c.xclk_freq_hz = 20000000;
//   c.pixel_format = PIXFORMAT_JPEG;
//   c.frame_size   = FRAME_SIZE;
//   c.jpeg_quality = JPEG_QUALITY;
//   c.fb_count     = 2;
//   c.fb_location  = CAMERA_FB_IN_PSRAM;
//   c.grab_mode    = CAMERA_GRAB_WHEN_EMPTY;

//   if (esp_camera_init(&c) != ESP_OK) {
//     Serial.println("Camera init failed (check PSRAM Enabled, power, and Sense board connection)");
//     while (true) delay(1000);
//   }

//   // ---- Wi-Fi connect (2.4 GHz only) ----
//   WiFi.mode(WIFI_STA);
//   WiFi.begin(WIFI_SSID, WIFI_PASS);
//   Serial.printf("Connecting to %s", WIFI_SSID);
//   int tries = 0;
//   while (WiFi.status() != WL_CONNECTED && tries < 60) { // ~30s
//     delay(500);
//     Serial.print(".");
//     tries++;
//   }
//   if (WiFi.status() != WL_CONNECTED) {
//     Serial.println("\nWiFi failed. Rebooting in 5s...");
//     delay(5000);
//     ESP.restart();
//   }

//   Serial.printf("\nReady. Open: http://%s/capture\n", WiFi.localIP().toString().c_str());

//   start_server();
// }

// void loop() {
//   // Optional: basic Wi-Fi watchdog to auto-reconnect
//   static unsigned long last = 0;
//   if (millis() - last > 5000) {
//     last = millis();
//     if (WiFi.status() != WL_CONNECTED) {
//       WiFi.disconnect();
//       WiFi.begin(WIFI_SSID, WIFI_PASS);
//     }
//   }
//   delay(10);
// }


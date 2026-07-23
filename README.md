# Industrial Energy Monitoring System

## Project Overview

The Industrial Energy Monitoring System is an Industrial IoT project developed to monitor electrical panel parameters and environmental conditions in real time. The system uses an ESP32 Master–Slave architecture with Modbus RTU (RS485) communication to collect data from multiple sensors, including the PZEM-004T energy meter, DHT22 temperature sensor, and MQ-2 gas sensor.

The ESP32 Master securely publishes sensor data to EMQX Cloud using MQTT TLS. A Python Backend subscribes to the MQTT messages, processes the incoming data, stores it in InfluxDB Cloud, and provides REST API services using Flask. The collected data is visualized through Grafana Dashboard, while ngrok is used to expose the REST API for external access during development and demonstration.

This project demonstrates the integration of embedded systems, industrial communication protocols, cloud services, databases, dashboards, and web APIs in a complete end-to-end Industrial IoT monitoring solution.


2. Key Features

3. System Architecture

4. Hardware Components

5. Software Stack

6. Project Structure

7. Communication Flow

8. Dashboard Preview

9. REST API

10. Demo Videos

11. Future Improvements

12. Author

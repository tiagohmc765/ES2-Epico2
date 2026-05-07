export class Measurement {
  constructor({
    id,
    batchId,
    temperature,
    humidity,
    luminosity,
    sensorOk = true,
    timestamp = new Date(),
    createdBy
  }) {
    this.id = id;
    this.batchId = batchId;
    this.temperature = temperature;
    this.humidity = humidity;
    this.luminosity = luminosity;
    this.sensorOk = sensorOk;
    this.timestamp = timestamp;
    this.createdBy = createdBy;
  }
}

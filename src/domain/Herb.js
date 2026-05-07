export class Herb {
  constructor({ id, name, scientificName, defaultLimits = null, createdAt = new Date() }) {
    this.id = id;
    this.name = name;
    this.scientificName = scientificName;
    this.defaultLimits = defaultLimits; // { tempMin, tempMax, humMin, humMax, lumMin, lumMax }
    this.createdAt = createdAt;
  }
}

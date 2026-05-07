import { createApp } from './app.js';
import { config } from './config/index.js';

const app = createApp();

app.listen(config.port, () => {
  // eslint-disable-next-line no-console
  console.log(`GREENHERB API a escutar em http://localhost:${config.port} (${config.env})`);
});

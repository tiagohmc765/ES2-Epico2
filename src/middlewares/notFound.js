export const notFound = (req, res) => {
  res.status(404).json({ error: 'Resource not found', path: req.originalUrl });
};

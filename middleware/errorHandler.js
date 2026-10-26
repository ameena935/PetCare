module.exports = (err, req, res, next) => {
  if (err.name === 'ValidationError') {
    return res.status(400).json({
      message: err.message
    });
  }

  if (err.name === 'CastError') {
    return res.status(400).json({
      message: 'Invalid id'
    });
  }

  console.error(err);
  res.status(500).json({
     message: err.message
  });
};
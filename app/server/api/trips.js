var express = require("express");
var Trip = require("../models/trip");

var router = express.Router();

router.get("/", (req, res) => {
    Trip.retrieveAll((err, trips) => {
    if (err) return res.json(err);
    return res.json(trips);
  });
});

module.exports = router;
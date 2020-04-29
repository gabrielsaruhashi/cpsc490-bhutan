var express = require("express");
var Facility = require("../models/facility");

var router = express.Router();

router.get("/", (req, res) => {
  Facility.retrieveAll((err, trips) => {
    if (err) return res.json(err);
    return res.json(trips);
  });
});

module.exports = router;

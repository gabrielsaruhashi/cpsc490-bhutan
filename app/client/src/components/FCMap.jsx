import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Card from "@material-ui/core/Card";

// fusioncharts
import FusionCharts from "fusioncharts";
import Maps from "fusioncharts/fusioncharts.maps";
import ReactFC from "react-fusioncharts";
import "../assets/jss/charts-theme";
import Bhutan from "fusioncharts/maps/fusioncharts.bhutan";

import { mean, average } from "stats-lite";

ReactFC.fcRoot(FusionCharts, Maps, Bhutan);

const useStyles = makeStyles({
  card: {
    backgroundColor: "#202a3b!important",
    padding: "1.5rem 1.5rem .75rem 1.5rem"
  },
  title: {
    fontSize: 14,
    color: "#8091ab",
    fontWeight: 400
  },
  pos: {
    marginBottom: 12
  },
  data: {
    fontWeight: "bold",
    color: "white"
  }
});

const FCMap = props => {
  const classes = useStyles();
  const { caption, data, subCaption } = props;

  const values = data.map(obj => obj.value);
  const maxValue = values.reduce((p, v) => (p > v ? p : v), 0);
  const medianValue = Math.round(mean(values));
  const minBound = medianValue - 50;

  return (
    <Card className={classes.card}>
      <ReactFC
        {...{
          type: "bhutan",
          width: "100%",
          height: "100%",
          dataFormat: "json",
          containerBackgroundOpacity: "0",
          dataEmptyMessage: "Loading Data...",
          dataSource: {
            chart: {
              theme: "ems",
              caption: `${caption}`,
              subCaption: `${subCaption}`
            },
            colorrange: {
              code: "#FFCC33",
              minvalue: "0",
              gradient: "1",
              color: [
                {
                  minvalue: 100,
                  maxvalue: `${medianValue}`,
                  code: "#FF4E12"
                },
                {
                  minvalue: `${medianValue}`,
                  maxvalue: `${maxValue}`,
                  code: "#020024"
                }
              ]
            },
            data: data
          }
        }}
      />
    </Card>
  );
};

export default FCMap;

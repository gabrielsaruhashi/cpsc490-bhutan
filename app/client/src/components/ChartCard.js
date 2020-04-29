import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Card from "@material-ui/core/Card";

// fusioncharts
import FusionCharts from "fusioncharts";
import Charts from "fusioncharts/fusioncharts.charts";
import ReactFC from "react-fusioncharts";
import "../assets/jss/charts-theme";

ReactFC.fcRoot(FusionCharts, Charts);

const useStyles = makeStyles({
  card: {
    backgroundColor: "#202a3b !important",
    borderLeft: "1px solid hsla(0,0%,100%,.1)!important",
    borderRight: "1px solid hsla(0,0%,100%,.1)!important",
    padding: "2em 0em"
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

const ChartCard = props => {
  const classes = useStyles();
  const { caption, data, color } = props;
  return (
    <Card className={classes.card}>
      <ReactFC
        {...{
          type: "doughnut2d",
          width: "300",
          dataFormat: "json",
          containerBackgroundOpacity: "0",
          dataSource: {
            chart: {
              caption: `${caption}%`,
              theme: "ems",
              defaultCenterLabel: `${data}%`,
              paletteColors: `${color}%`
            },
            data: [
              {
                label: "active",
                value: `${data}`
              },
              {
                label: "inactive",
                alpha: 5,
                value: `${100 - data}`
              }
            ]
          }
        }}
      />
    </Card>
  );
};

export default ChartCard;

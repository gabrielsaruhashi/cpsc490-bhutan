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

const Bar = props => {
  const classes = useStyles();
  const { caption, data, subCaption } = props;
  return (
    <Card className={classes.card}>
      <ReactFC
        {...{
          type: "bar2d",
          width: "100%",
          height: "100%",
          dataFormat: "json",
          containerBackgroundOpacity: "0",
          dataEmptyMessage: "Loading Data...",
          dataSource: {
            chart: {
              theme: "ems",
              caption: { caption },
              subCaption: { subCaption }
            },
            data: data
          }
        }}
      />
    </Card>
  );
};

export default Bar;

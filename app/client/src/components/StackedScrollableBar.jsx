import React, { Component } from "react";

import FusionCharts from "fusioncharts";
import charts from "fusioncharts/fusioncharts.charts";
import ReactFusioncharts from "react-fusioncharts";

// Resolves charts dependancy
charts(FusionCharts);

const dataSource = {
  chart: {
    caption: "Deaths reported because of insect bites in India",
    yaxisname: "Number of deaths reported",
    subcaption: "(As per government records)",
    flatscrollbars: "0",
    scrollheight: "12",
    numvisibleplot: "8",
    plottooltext:
      "<b>$dataValue</b> people died because of $seriesName in $label",
    theme: "fusion"
  },
  categories: [
    {
      category: [
        {
          label: "1994"
        },
        {
          label: "1995"
        },
        {
          label: "1996"
        },
        {
          label: "1997"
        },
        {
          label: "1998"
        },
        {
          label: "1999"
        },
        {
          label: "2000"
        },
        {
          label: "2001"
        },
        {
          label: "2002"
        },
        {
          label: "2003"
        },
        {
          label: "2004"
        },
        {
          label: "2005"
        },
        {
          label: "2006"
        },
        {
          label: "2007"
        },
        {
          label: "2008"
        },
        {
          label: "2009"
        },
        {
          label: "2010"
        },
        {
          label: "2011"
        },
        {
          label: "2012"
        },
        {
          label: "2013"
        },
        {
          label: "2014"
        },
        {
          label: "2015"
        },
        {
          label: "2016"
        },
        {
          label: "2017"
        }
      ]
    }
  ],
  dataset: [
    {
      seriesname: "Hymenoptera",
      data: [
        {
          value: "15622"
        },
        {
          value: "10612"
        },
        {
          value: "15820"
        },
        {
          value: "26723"
        },
        {
          value: "35415"
        },
        {
          value: "25555"
        },
        {
          value: "81803"
        },
        {
          value: "47950"
        },
        {
          value: "42396"
        },
        {
          value: "19435"
        },
        {
          value: "9780"
        },
        {
          value: "23243"
        },
        {
          value: "28619"
        },
        {
          value: "8477"
        },
        {
          value: "3503"
        },
        {
          value: "14278"
        },
        {
          value: "30522"
        },
        {
          value: "61518"
        },
        {
          value: "24819"
        },
        {
          value: "16437"
        },
        {
          value: "21171"
        },
        {
          value: "1690"
        },
        {
          value: "2418"
        },
        {
          value: "11253"
        }
      ]
    },
    {
      seriesname: "Diptera",
      data: [
        {
          value: "3622"
        },
        {
          value: "2612"
        },
        {
          value: "5820"
        },
        {
          value: "6723"
        },
        {
          value: "5415"
        },
        {
          value: "5555"
        },
        {
          value: "1803"
        },
        {
          value: "7950"
        },
        {
          value: "2396"
        },
        {
          value: "9435"
        },
        {
          value: "2780"
        },
        {
          value: "3243"
        },
        {
          value: "8619"
        },
        {
          value: "1477"
        },
        {
          value: "1503"
        },
        {
          value: "4278"
        },
        {
          value: "9522"
        },
        {
          value: "2518"
        },
        {
          value: "4819"
        },
        {
          value: "6437"
        },
        {
          value: "6171"
        },
        {
          value: "2690"
        },
        {
          value: "1418"
        },
        {
          value: "1253"
        }
      ]
    }
  ]
};

export default class StackedScrollableBar extends React.Component {
  render() {
    return (
      <ReactFusioncharts
        type="scrollstackedcolumn2d"
        width="100%"
        height="100%"
        dataFormat="JSON"
        dataSource={dataSource}
      />
    );
  }
}

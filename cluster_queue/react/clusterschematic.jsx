import React from 'react';
import ReactDOM from 'react-dom';

import Plot from 'react-plotly.js';

import css from '../assets/styles/cluster-schematic.sass'

function PercentageGauge(props) {
  return (
    <div className="progress-gauge vertical">
          <span className="text">
            {Math.round(props.value) + "%"}
          </span>
          <div className = "mask" style = {{ width: (100 - props.value) + "%" }} />
        </div>
  );
}

function Avatar(props) {
  if (typeof props.whom == 'undefined') {
    return null;
  } else {
    return (
      <img className="avatar-small" src={ "/static/avatars/"+ props.whom + ".png" } />
    );
  }
}

function ClusterCore(props) {
  return (
    <div className="cluster-core" style={{borderColor: props.color}}>
          <Avatar whom={props.avatar}/>
          <PercentageGauge value={props.cpu}/>
          <ActivityPlot/>
        </div>
  );
}

function ActivityPlot(props) {
  return (
    <Plot data={[{
            type: 'bar',
            x: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
           // y: [10, 20, 15, 30, 40, 50, 40, 70, 80, 80, 70],
            y: [10, 20, 15, 30, 40, 50, 40, 70, 80, 100, 100],
        marker: {
            color: 'rgb(128, 0, 60)',
        }
        }]}
              layout={{

                      xaxis: {
                          showticklabels : false,
                          tickvals : [5, 10],
                          range : [0, 10.5]
                      },
                      yaxis: {
                          showticklabels : false,
                          tickvals : [25, 50, 75, 100],
                          range : [0, 103],
                      },
                  showlegend: false,
                  autosize: false,
                  paper_bgcolor:'rgba(0,0,0,0)',
                  plot_bgcolor:'rgba(0,0,0,0)',
                  width: 73,
                  height: 30,
                  bargap: 0,
                  margin: {
                      l: 0,
                      r: 0,
                      b: 0,
                      t: 0,
                      pad: 10
                  },
              }} />
  );
}

class ClusterNetworkCanvas extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      cableStyles: {},
      packetStyles: {},
    };
  }

  componentDidMount() {
    const canvas = document.getElementById('cluster-schematic-canvas');
    const ctx = canvas.getContext('2d');

    this.setState({
      ctx: ctx
    }, () => {
      setInterval(this.drawNetworkLines.bind(this), 500);
    });
  }

  componentDidUpdate(prevProps) {
    if (this.props.activity !== prevProps.activity) {
      const newState = this.props.activity.reduce((result, row, row_id) =>
        row.reduce((
          result, job, col_id) => {

          // the cableStyles according to the cable colour
          var colr = job['color'];

          if (colr in result['cableStyles']) {
            result['cableStyles'][colr].push([row_id, col_id]);
          } else {
            result['cableStyles'][colr] = [
              [row_id, col_id]
            ];
          }
          // if there is a job id, then there should be network traffic
          if ('id' in job) {
            result['packetStyles']['white'].push([row_id, col_id]);
          }

          return result
        }, result), {
          'cableStyles': {},
          'packetStyles': {
            'white': []
          }
        });

      this.setState(newState);

    }
  }

  drawNetworkLines() {
    const gapLen = 275;
    var dashOffset =
      (Math.round((new Date()
        .getTime() / 1000) * 10)) % gapLen;

    this.doDrawNetworkLines(this.state.cableStyles, [0, 0], 3, 0);
    this.doDrawNetworkLines(this.state.packetStyles, [2, 50, 2, 25, 2, 200],
      2, dashOffset);
  }

  doDrawNetworkLines(styles, dashes, width, start_offset) {
    var ctx = this.state.ctx;

    ctx.lineWidth = width;
    ctx.setLineDash(dashes);

    Object.keys(styles)
      .map((key) => {
        ctx.beginPath();
        ctx.strokeStyle = key;

        styles[key].map((val) => {
          const row = val[0];
          const col = val[1];

          this.drawSingleNetworkLine(row, col, start_offset, ctx);
        });

        ctx.stroke();

      });

  }

  drawCorner(ctx, x, y, r, quartile) {
    const startAngle = (quartile - 1) / 2;

    ctx.arc(x, y, r, startAngle * Math.PI, (startAngle + 0.5) * Math
      .PI);
  }

  drawSingleNetworkLine(row, col, start_offset, ctx) {

    const xNetwork = 98.5 + 150 * col;
    const yNetwork = 27.5 + (223 * row);
    const xWidth = 60 - 10 * row;
    const yBottom = 900;
    const yBottomOffset = [30, 20, 10, 0];
    const xNetworkOffset = [0, -50, -80, -100];
    const heightFirstSegment = 12;
    const r = 5;

    ctx.moveTo(xNetwork, yNetwork + start_offset);
    ctx.arc(xNetwork + r, yNetwork - heightFirstSegment, r, Math.PI, 1.5 *
      Math.PI);
    ctx.arc(xNetwork + xWidth - r, yNetwork - heightFirstSegment, r, 1.5 *
      Math.PI, 2 * Math.PI);
    if (xNetworkOffset[row] != 0) {
      ctx.arc(xNetwork + xWidth - r, yBottom + yBottomOffset[row] - r, r, 0,
        0.5 * Math.PI);
      ctx.arc(xNetwork + xWidth + xNetworkOffset[row] + r,
        yBottom + yBottomOffset[row] + r,
        r, 1.5 * Math.PI, Math.PI, true);
    }
    ctx.lineTo(xNetwork + xWidth + xNetworkOffset[row], yBottom + 35);
  }

  render() {
    return (
      <canvas id="cluster-schematic-canvas" width="625px" height="976px"/>
    );
  }

}

class ClusterSchematic extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      // clusterLayout specifies how the cores are laid out in the cluster schematic
      clusterLayout: [
        [0, 1, 2, 3],
        [4, 5, 6, 7],
        [8, 9, 10, 11],
        [12, 13, 14, 15]
      ],
      defaultColour: "#e3e3e3",
      avatar_colors: [
        "#f26a44",
        "#3f3d31",
        "#d3ce3e",
        "#2eaeb7",
        "#fedb7d",
        "#2eaeb7",
        "#2eaeb7",
        "#fedb7d",
        "#d3ce3e",
        "#2eaeb7",
        "#fedb7d",
        "#2eaeb7",
        "#f26a44",
        "#2eaeb7",
        "#fffce9",
        "#f26a44",
        "#d3ce3e",
        "#3f3d31",
        "#d3ce3e",
        "#d3ce3e",
        "#fedb7d",
        "#3f3d31",
        "#fedb7d",
        "#2eaeb7",
        "#d3ce3e",
      ],
    };
  }

  render() {
    // map the cpu activity to each core
    const mappedActivity = this.state.clusterLayout.map((rows) => {
      return rows.map((core_id) => {
        var values = {
          cpu: this.props.cpuActivity[core_id],
        };

        // find the job running in this position (inefficient, but shouldn't matter)
        var job = this.props.running.find((job) => job.cores
          .includes(core_id))

        // if a job is running, give the job some values
        if (job) {
          values = {
            ...values,
            avatar: job['avatar'],
            color: this.state.avatar_colors[job['avatar'] - 1],
            name: job['name'],
            id: job['id']
          };
        } else {
            values['color'] = this.state.defaultColour;
        }

        return values;
      });
    });

    return (
      <div className="cluster-schematic">
        <ClusterNetworkCanvas activity={ mappedActivity }/>
      {
          mappedActivity.map((row, row_index) => {
              return (
                  <div key={row_index} className="cluster-row">
                  {
                      row.map((pi, col_index) => {
                          return (
                                <ClusterCore
                                  key={(row_index + 1)*(col_index + 1)}
                                  cpu={pi['cpu']}
                                  id={pi['id']}
                                  name={pi['name']}
                                  avatar={pi['avatar']}
                                  color={pi['color']}

                              />
                          );
                      })
                  }
                  </div>
              );
          })
      }
    </div>
    );
  }
}

export default ClusterSchematic;

import React from 'react';
import ReactDOM from 'react-dom';

import Plot from 'react-plotly.js';

import css from '../assets/styles/cluster-schematic.sass'

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
    <div className="cluster-core" style={{borderColor: props.colour}}>
          <Avatar whom={props.avatar}/>
          <ActivityPlot values={props.cpuHistory} colours={props.cpuColourHistory}/>
        </div>
  );
}

function ActivityPlot(props) {

  // don't attempt to plot anything if there is not value to plot
  if (typeof props.values == 'undefined') return null;

    const N = props.values.length;
    const x = Array.from(Array(N), (e,i) => i+1)
    const curr_colour = props.colours[props.colours.length - 1]

  return (
    <Plot
    style={{borderColor: curr_colour}}
        data={[{
            type: 'bar',
            x: x,
            y: props.values,
        marker: {
            color: props.colours,
        }
        }]}
    config={{staticPlot:true}}
              layout={{

                      xaxis: {
                          showticklabels : false,
                          tickvals : [],
                          range : [1, N + 0.5]
                      },
                      yaxis: {
                          showticklabels : false,
                          tickvals : [],
                          range : [0, 105],
                      },
                  showlegend: false,
                  autosize: false,
                  paper_bgcolor:'rgba(0,0,0,0)',
                  plot_bgcolor:'rgba(0,0,0,0)',
                  width: 121,
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
    if (this.props.info !== prevProps.info) {
      const newState = this.props.info.reduce((result, row, row_id) =>
        row.reduce((
          result, info, col_id) => {

          // the cableStyles according to the cable colour
          var colour = info.job.colour;

          if (colour in result['cableStyles']) {
            result['cableStyles'][colour].push([row_id, col_id]);
          } else {
            result['cableStyles'][colour] = [
              [row_id, col_id]
            ];
          }
          // if there is a info id, then there should be network traffic
          if ('id' in info) {
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

    const xNetwork = 148.5 + 170.5 * col;
    const yNetwork = 50.5 + (230 * row);
    const xWidth = 33 - 7 * row;
    const yBottom = 1000;
    const yBottomOffset = [30, 20, 10, 0];
    const xNetworkOffset = [0, -50, -80, -100];
    const r = 5;

    ctx.moveTo(xNetwork, yNetwork - r);
    ctx.arc(xNetwork + xWidth- r, yNetwork, r, 1.5 *
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
      <canvas id="cluster-schematic-canvas" width="695px" height="950px"/>
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
    };
  }

  render() {
    // map the cpu activity to each core
    const mappedInfo = this.state.clusterLayout.map((rows) => {
      return rows.map((core_id) => {
        return this.props.info[core_id]
      });
    });

    return (
      <div className="cluster-schematic">
        <ClusterNetworkCanvas info={ mappedInfo }/>
      {
          mappedInfo.map((row, row_index) => {
              return (
                  <div key={row_index} className="cluster-row">
                  {
                      row.map((node, col_index) => {
                          const job = node.job;

                          return (
                                <ClusterCore
                                  key={(row_index + 1)*(col_index + 1)}
                                  cpu={node['cpu']}
                                  cpuHistory={node['cpuHistory']}
                                  cpuColourHistory={node['cpuColourHistory']}
                                  id={job['id']}
                                  name={job['name']}
                                  avatar={job['avatar']}
                                  colour={job['colour']}

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

export { ClusterSchematic, Avatar };

import React from 'react';
import ReactDOM from 'react-dom';

import css from '../assets/styles/cluster-schematic.css'

function PercentageGauge(props) {
  return (
    <div className="progress-gauge">
          <span className="text">
            {Math.round(props.value) + "%"}
          </span>
          <div className = "mask" style = {{ width: (100 - props.value) + "%" }} />
        </div>
  );
}

function ClusterCore(props) {
  return (
    <div className="cluster-core">
          <PercentageGauge value={props.value}/>
        </div>
  );
}

class ClusterNetworkCanvas extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      cableStyles: {
        "blue": [
          [0, 0],
          [0, 1],
          [1, 0],
          [1, 1],
        ],
        "orange": [
          [0, 2],
          [0, 3],
          [1, 2],
          [1, 3],
        ],
        "#DDDDDD": [
          [2, 0],
          [2, 1],
          [2, 2],
          [2, 3],
          [3, 0],
          [3, 1],
          [3, 2],
          [3, 3],
        ]
      },
      packetStyles: {
        "white": [
          [0, 0],
          [0, 1],
          [0, 2],
          [0, 3],
          [1, 0],
          [1, 1],
          [1, 2],
          [1, 3],
        ]
      }
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

  drawNetworkLines() {
    const gapLen = 275;
    var dashOffset =
      (Math.round((new Date()
        .getTime() / 1000) * 10)) % gapLen;

    this.doDrawNetworkLines(this.state.cableStyles, [0, 0], 4, 0);
    this.doDrawNetworkLines(this.state.packetStyles, [5, 50, 5, 25, 5, 200],
      3, dashOffset);
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

    const xNetwork = 94.5 + 145 * col;
    const yNetwork = 19.5 + (165 * row);
    const xWidth = 60 - 10 * row;
    const yBottom = 655;
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
      <canvas id="cluster-schematic-canvas" width="600px" height="728px"/>
    );
  }

}

function ClusterSchematic(props) {
  return (
    <div className="cluster-schematic">
      <ClusterNetworkCanvas />
      {
          props.cpu_activity.map((row, row_index) => {
              return (
                  <div key={row_index} className="cluster-row">
                  {
                      row.map((val, col_index) => {
                          return (
                                <ClusterCore
                                  key={(row_index + 1)*(col_index + 1)}
                                  value={val}
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

export default ClusterSchematic;

import React from 'react';
import ReactDOM from 'react-dom';

import ClusterSchematic from './clusterschematic.jsx'

import Plot from 'react-plotly.js';

class Layout extends React.Component {
  constructor(props) {
    super(props);

    const cores = 12;

    this.state = {
      nCores: cores,
      cpuActivity: Array(cores)
        .fill(0),
      cpuActivityHistory: Array(cores)
        .fill(0)
        .map((v) => {
          return [v];
        }),
      maxNumHistoryEntries: 20,
      dataUrl: props.dataUrl,
      serverUpdateInterval: 5000,
      pending: [],
      running: [],
      coreMappings: [
        [0, 1, 2, 3],
        [4, 5, 6, 7],
        [8, 9, 10, 11],
        [12, 13, 14, 15]
      ],
    };

  }

  componentDidMount() {
    this.fetchActivity();
    setInterval(this.fetchActivity.bind(this), this.state
      .serverUpdateInterval);
  }

  // fetch best simulations from server and update in component state
  fetchActivity() {
    fetch(this.state.dataUrl)
      .then(res => res.json())
      .then(
        (result) => {
          const cpuHistory =
            this.state.cpuActivityHistory.map((series, index) => {
              const next_val = result['cpu_usage'][index];
              const nmax = this.state.maxNumHistoryEntries;
              return series.concat(next_val)
                .slice(series.length - nmax + 1, series.length + 1);
            });

          this.setState({
            cpuActivity: result['cpu_usage'],
            cpuActivityHistory: cpuHistory,
            pending: result['pending'],
            running: result['running'],

          });
        },
        (error) => {
          console.log("failed to load data from " + this.state.dataUrl);
        }
      );
  }

  render() {
    const cpuActivity = this.state.coreMappings.map((rows) => {
      return rows.map((core_id) => {
        return this.state.cpuActivity[core_id];
      });
    });

    return (
      <div id="layout">
        <div className="lhs-pane">
          <ClusterSchematic cpu_activity={cpuActivity} />
        </div>
        <div className="rhs-pane">
            <TimeLinePlot yValues={this.state.cpuActivityHistory} maxNumHistoryEntries={50} maxYValue={100}/>
          <h1 className="title is-2">Waiting</h1>
          <SimulationList simulations={this.state.pending}/>
          <h1 className="title is-2">Running</h1>
          <SimulationList simulations={this.state.running}/>
        </div>
      </div>
    );
  }
}

function SimulationList(props) {
  return props.simulations.map((sim) => {
    return <SimulationView key={sim['id']} simulation={sim}/>;
  });
}

function SimulationView(props) {

  const simulation = props.simulation;

  if (simulation == undefined) {
    return <div className="simulation-data"/>;
  } else {
    const sim_id = simulation['id'];

    const image_url = "simulations/" + sim_id +
      "/elmeroutput0001-velomagn.png";

    const image_alt = "Simulation " + sim_id + " image";

    return (
      <div className="simulation-data" style={{width: "30%", float : "left" }}>
            <p>
              {simulation['name']}
            </p>
              <img src={image_url}
                   alt={image_alt}
                   width="100%" />

            </div>
    );
  }
}

function TimeLinePlot(props) {
  const data = props.yValues.map((series, index) => {
    return {
      mode: 'lines',
      line: {},
      y: series,
    };
  });

  return (
    <div className="container">
        <Plot data={data}
                    layout={{

                        xaxis: {
                            title : 'Time',
                            showticklabels : false,
                            range : [0, props.maxNumHistoryEntries]
                        },
                        yaxis: {
                            title : 'Percentage',
                            range : [0, props.maxYValue]
                        },
                        showlegend: false,
                        width: '850px',
                        height: '200px',
                        title: 'CPU Vs Time'}}
              />
            </div>
  );
}

class AnimatedBarPlot extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      yValue: Array(props.nBars)
        .fill(0),
      targetYValue: props.targetYValue,
      easingStepSize: 5,
      maxYValue: props.maxYValue,
      easingUpdateInterval: 100,
      xValue: [...Array(props.nBars)
        .keys()
      ],
    };

    setInterval(this.updatePlotAnimation.bind(this), this.state
      .easingUpdateInterval);
  }

  updatePlotAnimation() {
    /* Moves yValue closer to yValueTarget by up to easingStepSize. This is to make transitions smoother (by limiting the movement permitted for each "frame"). Note that this implementation does mean bars don't finish moving at the same time, but it is simpler to implement with an external data source */
    const yValue = this.state.yValue.map((val, index) => {
      const diff = this.state.targetYValue[index] - val;
      const step = Math.sign(diff) * Math.min(this.state.easingStepSize,
        Math.abs(diff));
      return val + step;
    });
    this.setState({
      yValue: yValue
    });
  }

  render() {
    return (
      <div className="container">
        <Plot data={[{
                type: 'bar',
                x: this.state.xValue,
            y: this.state.yValue,
            marker : {
                color : this.state.yValue.map((y) => y/this.state.maxYValue ),
                /* note: default colorscales in src/components/colorscale/scales.js */
                colorscale: [[0, 'rgb(50,168,82)'],
                             [0.75, 'rgb(50,168,82)'],
                             [1, 'rgb(255,0,30)']]
            }
            }]}
              layout={{
                  xaxis: {
                      title : '',
                      showticklabels : false,
                  },
                  yaxis: {
                      title : 'Percentage',
                      range : [0, this.state.maxYValue]
                  },
                  width: '100%',
                  height: '100%',
                  title: 'CPU Usage'}}
        />
      </div>
    );
  }
}


ReactDOM.render(
  <Layout dataUrl={"/cluster/activity"} />,
  document.getElementById('root-activity')
);

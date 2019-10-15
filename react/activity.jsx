import React from 'react';
import ReactDOM from 'react-dom';
import {
  Avatar,
  ClusterSchematic
} from './clusterschematic.jsx'
import {
  SimulationList
} from './simulationlist.jsx'
import {
  colourJob
} from './receivesimulations.jsx'

import css from '../assets/styles/activity.sass'

class Layout extends React.Component {
  constructor(props) {
    super(props);

    const cores = 16;
    // map of labels provided by server to layout of the cluster
    // in the schematic in the client
    const clusterLayout = [
      ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4"],
      ["10.0.0.5", "10.0.0.6", "10.0.0.7", "10.0.0.8"],
      ["10.0.0.9", "10.0.0.10", "10.0.0.11", "10.0.0.12"],
      ["10.0.0.13", "10.0.0.14", "10.0.0.15", "10.0.0.16"]
    ];

    this.state = {
      clusterLayout: clusterLayout,
      nodeInfo: clusterLayout.map((row) =>
        row.map((col) => {
          return {
            job: {},
            cpuHistory: [],
            cpuColourHistory: []
          };
        })
      ),
      cpuHistoryMax: 50,
      dataUrl: props.dataUrl,
      serverUpdateInterval: 50,
      pending: [],
      running: [],
    };

  }

  componentDidMount() {
    window.addEventListener('load', this.startFetchActivity.bind(this));
  }

  buildJobMap(jobs) {
    // Build and returns a map of node_id -> job object from a joblist
    var job_map = {};

    jobs.forEach((job) => {
      job['cores'].forEach((node_id) => {
        job_map[node_id] = job;
      });
    });

    return job_map;
  }

  // start periodic poll of the cluster
  startFetchActivity() {
    this.fetchActivity();
    setInterval(this.fetchActivity.bind(this), this.state
      .serverUpdateInterval);
  }

  // fetch best simulations from server and update in component state
  fetchActivity() {
    fetch(this.state.dataUrl, {
        mode: 'cors'
      })
      .then(res => res.json())
      .then(
        (result) => {

          const running = result.running.map((job) => colourJob(job));
          const pending = result.pending.map((job) => colourJob(job));
          const job_map = this.buildJobMap(running);

          // map the cpu activity to each core
          const mappedInfo = this.state.clusterLayout.map((rows,
            row_idx) => {
            return rows.map((node_id, col_idx) => {
              var info = this.state.nodeInfo[row_idx][col_idx];

              const job = colourJob(job_map[node_id]);

              info.job = job;
              info.cpuHistory.push(result.cpu_usage[node_id]);
              info.cpuColourHistory.push(job.colour);

              // limit length to this.state.cpuHistoryMax
              const start = info.cpuHistory.length - this.state
                .cpuHistoryMax;
              const end = info.cpuHistory.length;

              if (start >= 0) {
                info.cpuHistory = info.cpuHistory.slice(start, end);
                info.cpuColourHistory = info.cpuColourHistory.slice(
                  start,
                  end);
              }

              return info;
            });
          });

          this.setState({
            nodeInfo: mappedInfo,
            pending: pending,
            running: running,

          });
        },
        (error) => {
          console.log("failed to load data from " + this.state.dataUrl);
        }
      );
  }

  render() {
    return (
      <div id="layout">
          <div className="pane lhs">
              <ClusterSchematic info={this.state.nodeInfo} />
          </div>
          <SimulationList simulations={this.state.running} title="Running" percentageKey='progress'/>
          <SimulationList simulations={this.state.pending} title="Waiting" percentageKey='progress'/>
      </div>
    );
  }
}

ReactDOM.render(
  <Layout dataUrl={"/cluster/activity"} />,
  document.getElementById('root-activity')
);

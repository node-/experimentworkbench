import React from 'react';
import Grid from '@material-ui/core/Grid'
import Paper from '@material-ui/core/Paper'
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import Tabs from '@material-ui/core/Tabs'
import axios from 'axios'
import Tab from '@material-ui/core/Tab'
import Dialog from '@material-ui/core/Dialog'
import DialogContent from '@material-ui/core/DialogContent'
import DialogActions from '@material-ui/core/DialogActions'
import ListSubheader from '@material-ui/core/ListSubheader';
import DeleteIcon from '@material-ui/icons/Delete'
import ListItemSecondaryAction from '@material-ui/core/ListItemSecondaryAction'
import Typography from '@material-ui/core/Typography'
import TextField from '@material-ui/core/TextField'
import ListItemText from '@material-ui/core/ListItemText'
import IconButton from '@material-ui/core/IconButton'
import Button from '@material-ui/core/Button'
import { withStyles } from '@material-ui/core/styles'
import { Slider } from '@material-ui/core';

import socketIOClient from "socket.io-client";

import './App.css';


const styles = theme => ({
  image: {
    width: "100%"
  },
  imageWrapper: {
    padding: "1rem"
  },
  configWrapper: {
    padding: "1rem"
  },
  deviceListWrapper: {
    padding: "1rem",
  },
  deviceItem: {
    '&:hover': {
      backgroundColor: "#d3d3d3",
      cursor: "pointer"
    } 
  }
})



class App extends React.PureComponent {
  state = {
    tab: 0,
    tab_viewport: 0,
    response: false,
    connected: false,
    endpoint: "http://127.0.0.1:3005",
    newDevice: {
      id: "",
      name: "",
      type: ""
    },
    addingDeviceDialog: false,

    // global config
    intervalTime: "",
    outputPath: "",
    frame: false,
    new_frame: false,
    devices: [],
    currentlySelectedDeviceId: false,
    cameraSettings: {
      exposure : 0,
      gain : 0,
      temp : 0,
      tint : 0
    },
  }

  componentDidMount() {
    const { endpoint } = this.state;
    const socket = socketIOClient(endpoint);

    socket.on("response", data => {
      this.setState({response: data});
      console.log(data);
    });

    socket.on("frame", data => {
      this.setState({new_frame: true});
      this.renderVideo();
    })

    socket.on("device_update", data => this.setState({devices: data.devices}))
    //socket.on("device_update", data => console.log(data.devices));
    socket.on('connect', () => {
      this.setState({connected: socket.connected})
    });

    socket.on('disconnect', () => {
      this.setState({connected: socket.connected})
    });
  }

  handleRemoveDevice = (device) => {
    //console.log(device);
  }

  handleCameraConfigSubmit = () => {
    this.setState({
      submitting: true
    })
    var set_device_url = "http://" + document.domain + ":3005/set_device/" + this.state.currentlySelectedDeviceId
    console.log(this.state.cameraSettings)
    axios.post(set_device_url, this.state.cameraSettings).then(response => {
      this.setState({
        submitting: false
      })
    })
    .catch(err => {
      console.log(err)
      this.setState({
        submitting: false
      })
    })
  }

  handleConfigSubmit = () => {
    this.setState({
      submitting: true
    })
    axios.post('http://localhost:3005/config', 
      {
        outputPath: this.state.outputPath,
        intervalTime: this.state.intervalTime,
      }
    )
    .then(response => {
      console.log(response.data)
      this.setState({
        submitting: false
      })
    })
    .catch(err => {
      console.log(err)
      this.setState({
        submitting: false
      })
    })
  }

  handleAddDevice = () => {
    this.setState({
      addingDeviceDialog: true
    })
  }

  handleCloseAddDevice = () => {
    this.setState({
      addingDeviceDialog: false,
      newDevice: {
        id: "",
        name: "",
        type: ""
      },
    })
  }

  handleDeviceChange = name => event => {
    this.setState({
      newDevice: {
        ...this.state.newDevice,
      [name]: event.target.value
      }
    })
  }

  handleConfigureCamera = name => event => {
    this.setState({
      cameraSettings: {
        ...this.state.cameraSettings,
      [name]: event.target.value
      }
    })
  }

  handleTextChange = name => event => {
    this.setState({
      [name]: event.target.value
    })
  }

  handleSelectDevice = device => _ => {
    this.setState({
      currentlySelectedDeviceId: device
    })
  }

  handleAddNewDevice = () => {
      axios.post('http://localhost:3005/add_device', this.state.newDevice).then(response => {
        //console.log(response.data)
        this.setState({
          submitting: false
        })
      })
      .catch(err => {
        console.log(err)
        this.setState({
          submitting: false
      })
    })
    this.setState({
      newDevice: {
        id: "",
        name: "",
        type: ""
      },
      addingDeviceDialog: false,
    })
  }

  renderAddDeviceDialog = () => {
    return (
      <Dialog open={this.state.addingDeviceDialog}>
        <DialogContent>
          <Typography>Name</Typography> 
          <TextField
            variant="outlined"
            fullWidth
            value={this.state.newDevice.name}
            onChange={this.handleDeviceChange('name')}
          />
          <Typography>ID</Typography> 
          <TextField
            variant="outlined"
            fullWidth
            value={this.state.newDevice.id}
            onChange={this.handleDeviceChange('id')}
          />
        <Typography>Type</Typography> 
          <TextField
            variant="outlined"
            fullWidth
            value={this.state.newDevice.type}
            onChange={this.handleDeviceChange('type')}
          />
        </DialogContent>
        <DialogActions>
          <Button 
            variant="contained"
            onClick={this.handleCloseAddDevice} color="secondary">Close</Button>
          <Button 
            onClick={this.handleAddNewDevice}
            variant="contained"
            color="primary">Submit</Button>
        </DialogActions>
      </Dialog>
    )
  }

  renderConfig = () => {
    const { classes } = this.props
    return (
      <div>
        <Paper className={classes.configWrapper}>
            <Typography>Config</Typography>
            <Typography align="left" variant="caption">Output Path</Typography>
            <TextField
              variant="outlined"
              fullWidth
              value={this.state.outputPath}
              onChange={this.handleTextChange('outputPath')}
            />
            <Typography align="left" variant="caption">Interval Time in Seconds</Typography>
            <TextField
              variant="outlined"
              fullWidth
              type="number"
              value={this.state.intervalTime}
              onChange={this.handleTextChange('intervalTime')}
            />
            <Button 
              disabled={this.state.submitting}
              onClick={this.handleConfigSubmit}
              fullWidth 
              variant="contained" 
              color="primary">Save</Button>
        </Paper>      
      </div>
    )
  }

  renderDevice = device => {
    const { classes } = this.props
    return (
      <ListItem 
        onClick={this.handleSelectDevice(device.id)}
        className={classes.deviceItem}
        selected={this.state.currentlySelectedDeviceId === device.id}
        key={device.id}>
        <ListItemText primary={device.name} secondary={device.id} />
        <ListItemSecondaryAction>
          <IconButton onClick={this.handleRemoveDevice(device)} >
            <DeleteIcon />
          </IconButton>
        </ListItemSecondaryAction>
      </ListItem>
    )
  }

  renderVideo = () => {
    const { classes } = this.props
    const { frame } = this.state
    var image_url = "http://" + document.domain + ":3005/frame/" + this.state.currentlySelectedDeviceId + "?t=" + Date.now() 
    return (
      <div className={classes.imageWrapper}>
          <img 
            className={classes.image}
            alt="cam" src={image_url} /> 
      </div>
    )
  }

  renderDeviceList = () => {
    const { classes } = this.props
    const { devices } = this.state
    return (
      <div className={classes.deviceListWrapper}>
        <Paper square>
          <List
            subheader={<ListSubheader>Device List</ListSubheader>} 
          >
            {devices.map(d => this.renderDevice(d))}
          </List>
          <div style={{padding: "0.5rem"}}>
            <Button 
              onClick={this.handleAddDevice}
              color="primary" variant="contained">Add</Button>
          </div>
        </Paper>
        {this.renderCameraConfig()}
      </div>
    )
  }

  handleTabChange = (_, newValue) => {
    this.setState({
      tab: newValue
    })
  }

  handleViewportChange = (_, newValue) => {
    this.setState({
      tab_viewport: newValue
    })
  }

  renderViewport = () => {
    const { tab_viewport } = this.state
    return (
      <div>
        <Tabs
          variant="fullWidth"
          value={tab_viewport}
          onChange={this.handleViewportChange}
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab label="Viewport 0" />
          <Tab label="Viewport 1" />
        </Tabs>
        {
          tab_viewport === 0 && this.renderVideo()
        }
        {
          tab_viewport === 1 && this.renderVideo()
        }
      </div>
    )
  }

  renderMenu = () => {
    const { tab } = this.state
    return (
      <div>
        <Tabs
          variant="fullWidth"
          value={tab}
          onChange={this.handleTabChange}
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab label="Device List" />
          <Tab label="Config" />
        </Tabs>
        {
          tab === 0 && this.renderDeviceList()
        }
        {
          tab === 1 && this.renderConfig()
        }
      </div>
    )
  }

  renderConnectionInfo = () => {
    const { connected } = this.state;
    const text = connected ? "Connected" : "Not Connected";
    const color = connected ? "primary" : "secondary";
    return (
        <Grid item xs>
          <Button color={color} variant="contained" fullWidth>{text}</Button>
        </Grid>
    )
  }

  renderCameraConfig = () => {
    const { classes } = this.props
    const { currentlySelectedDeviceId } = this.state
    var value = 0;

    // todo: curry
    // onChange={handleCamConfigChange("exposure")}

    return (
      <Paper className={classes.configWrapper}>
        <Grid item>
          <Typography id="non-linear-slider" gutterBottom>
            Exposure Time
          </Typography>
          <Slider 
            onChange={this.handleConfigureCamera("exposure")}
            value={this.state.cameraSettings.exposure} 
            aria-labelledby="continuous-slider" 
            max={2000000}
            min={400}
          />

          <Typography id="non-linear-slider" gutterBottom>
            Exposure Gain
          </Typography>
          <Slider 
            onChange={this.handleConfigureCamera("gain")}
            value={this.state.cameraSettings.gain} 
            aria-labelledby="continuous-slider" 
            max={300}
            min={100}
          />

          <Typography id="non-linear-slider" gutterBottom>
            White Balance Temperature
          </Typography>
          <Slider 
            onChange={this.handleConfigureCamera("temp")}
            value={this.state.cameraSettings.temp} 
            aria-labelledby="continuous-slider" 
            max={15000}
            min={2000}
          />

          <Typography id="non-linear-slider" gutterBottom>
            White Balance Tint
          </Typography>
          <Slider 
            onChange={this.handleConfigureCamera("tint")}
            value={this.state.cameraSettings.tint} 
            aria-labelledby="continuous-slider" 
            max={2500}
            min={200}
          />

          <Typography id="non-linear-slider" gutterBottom>
            Rotation
          </Typography>
          <Slider 
            onChange={this.handleConfigureCamera("rotation")}
            value={this.state.cameraSettings.rotation} 
            aria-labelledby="continuous-slider" 
            max={360}
            min={0}
          />


          <Button 
            color="primary" 
            variant="contained"
            disabled={this.state.submitting}
            onClick={this.handleCameraConfigSubmit}
            fullWidth 
          >Submit</Button>
        </Grid>
      </Paper>
    )
  }

  render = () => {
    // const { classes } = this.props
    return (
      <div className="App">
        <header className="App-header">
          <Grid container>
            <Grid item xs={12} md={8}>
              {this.renderViewport()}
            </Grid>
            <Grid item xs={12} md={4}>
              {this.renderMenu()}
              {this.renderConnectionInfo()}
            </Grid>
          </Grid>
        </header>
        {this.renderAddDeviceDialog()}
      </div>
    );
  }
}

export default withStyles(styles)(App)
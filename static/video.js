var socket = io()

window.onload = () => {
    start_spookystream();
}

//
// Pose estimation functions
//

// See https://github.com/tensorflow/tfjs-models/tree/master/pose-detection

let model, detector;

async function initPoseDetection() {
  console.log("Loading pose detection models")
  model = poseDetection.SupportedModels.MoveNet;
  detector = await poseDetection.createDetector(
    poseDetection.SupportedModels.MoveNet,
    { 
      quantBytes: 4,
      outputStrite: 16,
      inputresolution: { width: renderedcanvas.width, height: renderedcanvas.height },
      multiplier: 0.75
    }
  );
  console.log("Loaded pose detection models")
}

async function estimatePose(image) {
  poses = await detector.estimatePoses(image);
  return poses;
}

// Drawing functions
function drawKeypoints(pose) {
  pose.keypoints.forEach(keypoint => {
    // If the key point is above a specific confidence
    if (keypoint.score > 0.6) {
      // Place a rectangle centered over the spot it was detected
      renderedcontext.fillStyle = "#00FF00";
      renderedcontext.fillRect(keypoint.x -2 | 0, keypoint.y -2 | 0, 4, 4);  

      // Write the name of the detected keypoint next to the detected spot
      renderedcontext.font = "8px Arial";
      renderedcontext.textAlign = "left"
      renderedcontext.fillText(keypoint.name, keypoint.x+8, keypoint.y)
    }
  })
}


let facepositionnames = ['nose','left_eye','right_eye','left_ear','right_ear']
function getFaceRectangle(pose) {
  // Filter out face features and nything below a score of 0.6

  // This is somewhat slow?
  //faceCoords = pose.keypoints.filter(p => facepositionnames.includes(p.name) && p.score > 0.6 )
  
  // If no poses are found return null (And don't log to the console that it's undefined.
  if ( pose === null || pose === undefined) return null;

  // To make it faster include the below loop
  faceCoords = []
  for (let i = 0; i < 5; i++) {
    if (pose.keypoints[i].score > 0.6) {
      faceCoords.push(pose.keypoints[i]) 
    }
  }

  // find the bounding box of those coordinates
  if (faceCoords.length > 1) {
    return faceCoords.reduce(function(p,c) {
       x = c.x | 0
       y = c.y | 0

      return {
        minx: p.x < x ? p.x : x | 0,
        miny: p.y < y ? p.y : y | 0,
        maxx: p.x > x ? p.x : x | 0,
        maxy: p.y > y ? p.y : y | 0
      }
    })
  } else {
    return null
  }
}

function drawFaceRectangle(pose) {
  box = getFaceRectangle(pose)

  if (box) {
    renderedcontext.fillStyle = "#FF0000";
    renderedcontext.fillRect(box.minx, box.miny, box.maxx-box.minx, box.maxy-box.miny);  
  }
}

// Create an array containing the last 30 positions, we'll use this to create some smoothing
let lastdots = Array(30).fill([0,0])

function drawFaceDot(pose) {
  // Find the face in the image
  box = getFaceRectangle(pose)

 // If a face is found
  if (box) {
    // Shift removes the first element, then add our current box coords to the end
    lastdots.shift()
    lastdots.push([box.minx,box.miny])
  }
  // Draw a 4x4 dot on the last known position, we can use the same location to aim later
  renderedcontext.fillStyle = "#FF0000";
  renderedcontext.fillRect(lastdots[lastdots.length-1][0], lastdots[lastdots.length-1][1], 4, 4);  
}


function drawPoses(poses) {
    // Draw the video frame to the rendered context -- this is a different frame from what the pose detection was completed on
    renderedcontext.globalCompositeOperation = 'normal'
    renderedcontext.drawImage(videoElement,0,0)

    // For each pose that was detected
    //poses.forEach(pose => {
    //  drawKeypoints(pose);
    //  drawFaceRectangle(pose);
    //})

    // Limit to one pose and one dot for now
    drawFaceDot(poses[0])
}


//
// Video element handling
//

// Incoming webcam video
videoElement = document.querySelector('#spookystream');

// Canvas to display and output the result to screen too
const renderedcanvas = document.querySelector('#renderedcanvas');
const renderedcontext = renderedcanvas.getContext('2d');

// Function to grab an image from the videoElement, perform processing, 
// then display it in the canvas
let previousTimeStamp;

// renderVideo
function renderVideo(timestamp) {
    // If this timestamp is the same is the previous, we've called this function before the image has had a chance to update.
    if (previousTimeStamp !== timestamp) {
      // Estimate a pose from the image stream, draw the results
      estimatePose(videoElement).then((poses) => { drawPoses(poses) })

      // Save this timestamp so we can check if we're trying to render too fast.
      previousTimeStamp = timestamp
    }

    // Request that this function gets called on the next render
    // This appears to be called on every monitor refresh, faster than the video is updating, the timestamps should sort this out.
    requestAnimationFrame(renderVideo)
  }

//
// Manual controls
//
const controlsEnabled = document.querySelector('#controlsEnabled');
const verticalSlider = document.querySelector('#verticalSlider');
const horizontalSlider = document.querySelector('#horizontalSlider');
const lidSlider = document.querySelector('#lidSlider');

const lidServoHalfClose = document.querySelector('#lidServoHalfClose');
const lidServoClose = document.querySelector('#lidServoClose');

const lidSmallMovementThreshold = document.querySelector('#lidSmallMovementThreshold');
const lidLargeMovementThreshold = document.querySelector('#lidLargeMovementThreshold');

const movementDisplay = document.querySelector('#movementValue');

// Detect when there is movement, then open the lid, setTimeout to close the lid again.
let lidposition = 1.0 // closed by default
let lidTimer = null
let movements = Array(20).fill(0)

function lidBehaviour() {
  // Calculate distance from last movement
  var diffx = lastdots[9][0] - lastdots[10][0];
  var diffy = lastdots[9][1] - lastdots[10][1];
  var distance = Math.sqrt(Math.pow(diffx + diffy, 2));

  // Pythagoras! 
  distance = Math.sqrt(Math.pow(diffx + diffy, 2));

  movements.shift();
  movements.push(distance);

  movementDisplay.textContent = movements[-1].toString();

  var totalmovements = movements.reduce((curr, prev) => Math.abs(prev-curr));

  // If there's some movement over the thresold
  if (movements[-1] > lidLargeMovementThreshold.value) {
    // Open the lid
    lidposition = 0.15; // full open

    // Then check if a timer has been set already to close the lid
    if (!lidTimer) {
      // Clear the existing timer
      clearTimeout(lidTimer);
    }
    // Set a new timer to close the lid 2 seconds after any movements.
    lidTimer = setTimeout(closeLid, 2000);
  }
}

function closeLid() {
  lidposition = lidServoClose.value/(lidServoClose.max * 1.0);
  lidTimer = null
}

//
// Send the locations to spookybox
//
function sendToSpookyBox() {
  // Called on a timer.
  // message format is [x, y, lidposition].
  // where each value is a number between 0 and 1 representing the fraction of the total
  // amount of movement the servo has.

  var locationx = 0.0 // 1.0 is right, 0.0 is left from the boxes point of view
  var locationy = 0.0 // 0.0 is up, 1.0 is down
  var lid = 1.0 // 1.0 is closed, 0.0 is open.

  if (controlsEnabled.checked == true) {
    locationx = 1.0 - (horizontalSlider.value / (horizontalSlider.max * 1.0))
    locationy = verticalSlider.value / (verticalSlider.max * 1.0)
    lid = lidSlider.value / (lidSlider.max * 1.0)
  } else {
    // X is reversed, Y is not
    locationx = (renderedcanvas.width - lastdots[lastdots.length-1][0]) / renderedcanvas.width
    locationy = lastdots[lastdots.length-1][1] / renderedcanvas.height
    lid = lidposition
  }

  socket.emit('faceposition', [locationx, locationy, lid])
}
  

async function start_spookystream() {
  // Init socket.io
  socket.on('connect', function() { socket.emit('event', {'data': "Connected!"})})

  // Init pose detection
  await initPoseDetection();

  // Set the render output side to the video size
  renderedcanvas.width = videoElement.width;
  renderedcanvas.height = videoElement.height;

  // Set a loading message in the canvas (not working)
  renderedcontext.fillStyle = "green"
  renderedcontext.font = "30px Arial";
  renderedcontext.textAlign = "center";
  renderedcontext.fillText("Loading...", renderedcanvas.width/2, renderedcanvas.height/2);

  // Trigger the start of processing.
  renderVideo();

  // Update spookybox 10 times a second
  setInterval(sendToSpookyBox, 100)
  // Check our lid behaviour 10 times a second
  setInterval(lidBehaviour, 100)
}

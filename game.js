//The MIT License
//
//Copyright 2017 - Cesar Saez <hi@cesarsaez.me>
//
//Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
//associated documentation files (the "Software"), to deal in the Software without restriction,
//including without limitation the rights to use, copy, modify, merge, publish, distribute,
//sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
//furnished to do so, subject to the following conditions:
//
//The above copyright notice and this permission notice shall be included in all copies or
//substantial portions of the Software.
//
//THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
//NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
//NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
//DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
//OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


var canvas = document.getElementById("game");
var ctx = canvas.getContext("2d");

// entities
var world = {
  screen: 0,        // 0: welcome, 1: game, 2: game over
  gap_size: 15,     // lines
  vel: -3,          // horizontal scroll
  gravity: 1,
  line_height: 10,
  key_strength: 18,
  FPS: 30,
  frame: 0,
  obstacles: new Array(3)
}

var player = {
  score: 0,
  vel: 0,
  posx: canvas.width * 0.25,
  posy: 0,
  sprite: function() {
    if (this.vel < -5) {
      retval = ["   . 7", " // _\/"];    // up
    } else if (this.vel > 5) {
      retval = ["\\\\ .", " \\\\__\\"];  // down
    } else {
      retval = ["   (.", "==  __>"];     // center
    };
    return(retval);
  }
}

var obstacle = {
  posx: canvas.width,
  height: 5,  // lines
  sprite: []
}

function gen_pipe_sprite(each_pipe) {
  retval = new Array(each_pipe.height - 2).fill("|   |");
  retval.push("=====");
  retval.push("=====");

  gap = new Array(world.gap_size).fill("");
  retval = retval.concat(gap);

  retval.push("=====");
  retval.push("=====");
  bottom_length = (canvas.height * .1) - retval.length;
  bottom = new Array(bottom_length).fill("|   |");
  retval = retval.concat(bottom);
  return(retval);
}

window.onload=function() {
  init_game();
  document.addEventListener("keydown", keyPush);
  document.addEventListener("mousedown", keyPush);
  setInterval(game, 1000/world.FPS)
}

function keyPush(event) {
  if (world.screen == 1) {
    player.vel = - world.key_strength * world.gravity;
  } else if(world.frame > 10) {  // wait 10 frames before restart
    init_game();
    world.screen = 1;
  }
}

function init_game() {
  player.posy = 0;
  player.vel = 0;
  player.score = 0;
  world.frame = 0;
  world.screen = 0; // welcome
  for (var i=0; i<3; i++) {
    var each_pipe = JSON.parse(JSON.stringify(obstacle)); // clone
      var height = Math.floor((canvas.height * Math.random()) / (2 * world.line_height));
    each_pipe.height = height + 2;
    each_pipe.posx = canvas.width + (i * canvas.width / 2);
    each_pipe.sprite = gen_pipe_sprite(each_pipe);
    world.obstacles[i] = each_pipe;
  }
}

function clear_screen() {
  ctx.fillStyle = "black";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "white";
  ctx.font = `${world.line_height}px Courier`;
}

function draw_score() {
  ctx.fillStyle = "black";
  ctx.fillRect(canvas.width - 100, 0, canvas.width, world.line_height);
  ctx.fillStyle = "white";
  ctx.font = `${world.line_height}px Courier`;
  ctx.fillText(`score: ${player.score}`, canvas.width - 100, world.line_height);
}

function game() {
  if (world.screen == 0) {
    welcome();
  } else if(world.screen == 1) {
    game_loop();
  } else {
    game_over();
  }
  world.frame += 1;
}

function welcome() {
  clear_screen();
  text = [
    "  __ _                _ _   _     _         _ ",
    " / _| |              (_|_) | |   (_)       | |",
    "| |_| | __ _ ___  ___ _ _  | |__  _ _ __ __| |",
    "|  _| |/ _` / __|/ __| | | | '_ \\| | '__/ _` |",
    "| | | | (_| \\__ \\ (__| | | | |_) | | | | (_| |",
    "|_| |_|\\__,_|___/\\___|_|_| |_.__/|_|_|  \\__,_|",
  ];
  for (var i=0; i<text.length; i++) {
    ctx.fillText(text[i], canvas.width/2 - 140, canvas.height/2 + (i*10) - 40);
  }
  // blinking message
  if (world.frame < world.FPS) {
    ctx.fillText("Press any key to start", canvas.width/2 - 65, canvas.height/2 + 30);
  }
  if (world.frame > 1.3 * world.FPS) world.frame = 0;
}

function game_loop() {
  clear_screen();

  // backgroud
  var obstacle = null;
  for (var i=0; i < world.obstacles.length; i++) {
    var each_pipe = world.obstacles[i];
    each_pipe.posx += world.vel;
    if (each_pipe.posx + 30 > player.posx && each_pipe.posx < player.posx + 38) {
      obstacle = each_pipe;
    }
    for (var j=0; j<world.obstacles[i].sprite.length; j++) {
      ctx.fillText(each_pipe.sprite[j], each_pipe.posx,
        world.line_height + (j*world.line_height));
    };
    // re-purpose offscreen elements
    if (each_pipe.posx < -50) {
      each_pipe.posx += 1.5 * canvas.width;
    }
  }

  // player
  player.vel += world.gravity;
  player.posy += player.vel;
  player.sprite().forEach(function(item, index, array) {
    ctx.fillText(item, canvas.width/4, player.posy + (10*index));
  });

  player.score = world.frame;
  draw_score();

  // game over?
  var isTooHigh = player.posy < 0;
  var isTooLow = player.posy + 20 > canvas.height;
  if (obstacle != null) {
    isTooHigh = player.posy < obstacle.height * world.line_height;
    isTooLow = player.posy > (obstacle.height + world.gap_size) * world.line_height;
  }
  if (isTooHigh || isTooLow) {
    world.frame = 0;
    world.screen = 2;
  }
}

function game_over() {
  clear_screen();
  text = [
    "  __ _  __ _ _ __ ___   ___    _____   _____ _ __ ",
    " / _` |/ _` | '_ ` _ \\ / _ \\  / _ \\ \\ / / _ \\ '__|",
    "| (_| | (_| | | | | | |  __/ | (_) \\ V /  __/ |   ",
    " \\__, |\\__,_|_| |_| |_|\\___|  \\___/ \\_/ \\___|_|   ",
    "  __/ |                                           ",
    " |___/  ",]
  for (var i=0; i<text.length; i++) {
    ctx.fillText(text[i], canvas.width/2 - 150,
      canvas.height/2 + (i*world.line_height) - 2*world.line_height);
  }
  draw_score();

  // back to welcome screen after 5 secs
  if (world.frame > 5 * world.FPS) {
    world.frame = 0;
    world.screen = 0;
  }
}

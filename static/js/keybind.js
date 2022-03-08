document.addEventListener('keydown', function(e){
    if(!e.repeat){
        key = e.key.toLowerCase()
        if (key === 'w' && e.shiftKey){
            console.log('Move forward fast')
            new_ajax_helper('/moveforward');
        }
        else if (key === 's' && e.shiftKey){
            console.log('Move backward fast')
            new_ajax_helper('/movebackwards');
        }
        else if (key === 'w'){
            console.log('Move forward')
            new_ajax_helper('/moveforwardslowly');
        }
        else if (key === 'a'){
            console.log('Turn Left')
            new_ajax_helper('/turnleft');
        }
        else if (key === 'd'){
            console.log('Turn right')
            new_ajax_helper('/turnright');
        }
        else if (key === 's'){
            console.log('Move backwards')
            new_ajax_helper('/movebackwardsslowly');
        }
        else if (key === 'o'){
            console.log('shoot')
            new_ajax_helper('/shoot');
        }
        else if (key === 'l'){
            console.log('shoot')
            new_ajax_helper('/shoot');
        }
    }
})

document.addEventListener('keyup', function(e){
    key = e.key.toLowerCase()
    if (e !== o && e !== l){
        console.log('stop')
    new_ajax_helper('/stop');
    }
})
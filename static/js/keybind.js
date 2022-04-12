var sport = false;

document.addEventListener('keydown', function(e){
    if(!e.repeat){
        key = e.key.toLowerCase()
        if (key === 'p'){
            if (sport == false){
                sport = true;
            }
            else if (sport == true) {
                sport = false;
            }
        }
        if (sport === true){
            if (key === 'w'){
            console.log('Move forward fast')
            new_ajax_helper('/moveforward');
            }
            else if (key === 's'){
                console.log('Move backward fast')
                new_ajax_helper('/movebackwards');
            }
            else if (key === 'a'){
                console.log('Turn Left fast')
                new_ajax_helper('/turnleft');
            }
            else if (key === 'd'){
                console.log('Turn right fast')
                new_ajax_helper('/turnright');
            }
        }
        else if (sport === false){
            if (key === 'd'){
                console.log('Turn right')
                new_ajax_helper('/turnrightslow');
            }
            else if (key === 'a'){
                console.log('Turn Left')
                new_ajax_helper('/turnleftslow');
            }
            else if (key === 'w'){
                console.log('Move forward')
                new_ajax_helper('/moveforwardslow');
            }
            else if (key === 's'){
                console.log('Move backwards')
                new_ajax_helper('/movebackwardsslow');
            }
        }
        if (key === 'o'){
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
    if (key !== 'o' && key !== 'l'){
        console.log('stop')
        new_ajax_helper('/stop');
    }
})
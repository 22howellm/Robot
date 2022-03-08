document.addEventListener('keydown', function(e){
    if(!e.repeat){
        if (e.key === 'w'){
            console.log('Move forward')
        }
        if (e.key === 'a'){
            console.log('Turn Left')
        }
        if (e.key === 'd'){
            console.log('Turn right')
        }
        if (e.key === 's'){
            console.log('Move backwards')
        }
        if (e.key === 'w' && e.shiftKey){
            console.log('Move forward fast')
        }
        if (e.key === 's' && e.shiftKey){
            console.log('Move backward fast')
        }
    }
})
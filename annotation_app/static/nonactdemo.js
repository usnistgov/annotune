const intro = introJs();

intro.setOptions({
    steps: [
        {
            intro: "This demo will introduce you the key notes of this page"
        },
        
        {
            element: '#home',
            intro: 'This takes you to the previous page with instructions'
        },
        {
            element: '#topicblock',
            intro: 'This is a topic block. It has a topic number, keywords related to the topic and documents associated with the topic.'
        },
        {
            element: '#recommended_table',
            intro: 'The recommeded document from the model is displayed first'
        },
        {
            element: '#demo',
            intro: 'Click this button if you want to go through this demo again'
        }
    
    ]
})

// const hasRunIntro = localStorage.getItem("hasRunIntro");
// if (hasRunIntro !== "1"){
//     intro.start();
//     localStorage.setItem("hasRunIntro", "1");
// }
document.getElementById("demo").addEventListener('click', function(){
    intro.start();
})
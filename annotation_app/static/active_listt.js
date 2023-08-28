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
            element: '#completed',
            intro: 'A completed button appears on the navigation bar after labelling two documents. This displays your labeled documents'
        },
        {
            element: '#act_lis',
            intro: 'Thos block has all the document to be labeled'
        },
        {
            element: '#recommended',
            intro: 'This is the recommended document to be labeled by the model'
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

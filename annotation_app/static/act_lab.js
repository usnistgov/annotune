const intro = introJs();

intro.setOptions({
    steps: [
        {
            element: '#documents',
            intro: 'This is how you get back to the list of documents'
        },
       
        {
            element: '#model_sugges',
            intro: "This is where you label the document. You can either type a label or select your old labels from the dropdown"
        },
        {
            element: '#myBtn',
            intro: 'Submit button takes you to the next recommended document by the model. You can always use the document button to view the list of all documents'
        },
        {
            element: '#completed',
            intro: 'A completed button appears after labeling one document. This takes display your labeled documents'
        },
        {
            element: '#demo',
            intro: 'Click this button if you want to go through this demo again'
        }
    ]
})

const hasRunIntro = localStorage.getItem("hasRunIntro");
if (hasRunIntro !== "1"){
    intro.start();
    localStorage.setItem("hasRunIntro", "1");
}

document.getElementById("demo").addEventListener('click', function(){
    intro.start();

})

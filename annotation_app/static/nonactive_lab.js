const intro = introJs();

intro.setOptions({
    steps: [
        {
            element: '#documents',
            intro: 'This is how you get back to the list of documents'
        },
        {
            element: '#model_suggestion',
            intro: 'The suggested label from the model. It starts after two labels'
        },
        {
            element: '#model_sugges',
            intro: "This is where you label the document. You can either type a label or select your old labels from the dropdown"
        },
        {
            element: '#topic11',
            intro: 'This block has the topic and the keywords associated to the topic'
        },
        {
            element: '#buttons',
            intro: 'You can highlight the keywords that are common to topic and the document.'
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


const viewButtons = document.querySelectorAll(".view");
textcontents= document.getElementById("text")
oritextElement=document.getElementById("original_text");
oritextElements=document.getElementById("original_text");
// console.log(textElement.innerText)
const original_texts = oritextElement.innerText;
var markInstance = new Mark(document.getElementById("text"));
const getButtons = document.querySelectorAll(".view");
// var  = btn.parentElement.nextElementSibling.getElementsByTagName("span");
// var keyword = btn.parentElement.nextElementSibling.getElementsByTagName("span");

function performMark(keywords) {

  // Read the keyword
//   var keywords = btn.parentElement.nextElementSibling.getElementsByTagName("span");
//   console.log(keywords)

  // Determine selected options
  var options = {
    "separateWordSearch": false,
    "diacritics": true
  };
  

  // Remove previous marked elements and mark
  // the new keyword inside the context
  markInstance.unmark({
  	done: function(){
    	markInstance.mark(keywords);
    }
  });
};
var options = {
    "separateWordSearch": false,
    "diacritics": true
  };

// Listen to input and option changes
num = 0
viewButtons.forEach((btn, index) => {
  btn.addEventListener("click", function(event){
    var keywords = btn.parentElement.nextElementSibling.getElementsByTagName("span");
    const wordsArr = [];
    Array.from(keywords).forEach(function (ele) {
        if (ele.innerText.length > 3){
            wordsArr.push(ele.innerText);
            // console.log(ele.innerText)
        }
    });
    let joint_keywords = wordsArr.join(" ")
    if (num % 2 == 0){
        markInstance.mark(wordsArr, options);
    }
    else{
        markInstance.unmark(wordsArr, options);
        textcontents.innerText = original_texts
        
    }
    num = num +1
    // console.log(wordsArr.join(" "))
    
    // console.log(joint_keywords)
    

  });
});





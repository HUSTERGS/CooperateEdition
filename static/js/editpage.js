var viewpannel = document.querySelector(".view");
var changeset = new Object();
changeset.actions = new Array();
changeset.version = 0;
doc = document.querySelector("textarea");
//docdata = eval(doc.getAttribute("d"));

/*
doc.addEventListener("input", e => {
  changeset.actions.push({
    type: e.inputType.slice(0, 6),
    content: e.data,
    index:
      e.inputType.slice(0, 6) === "insert"
        ? doc.selectionStart - 1
        : doc.selectionStart + 1
  });
  //console.log(changeset.actions)
  //console.log(JSON.stringify(changeset))
});
//请求最新版本

rqversion();

function rqnewestdoc() {
  fetch("/root/first trial/rqnewestdoc", {
    method: "POST",
    body: JSON.stringify(changeset.version)
  }).then(res =>
    res.json().then(data => {
      if (data) doc.value = data;
    })
  );
}
function firstdoc() {
  fetch("/root/first trial/firstdoc", {
    method: "GET"
  }).then(res =>
    res.json().then(data => {
      doc.value = data;
    })
  );
}
//请求版本号
function rqversion() {
  fetch("/root/first trial/requestversion", {
    method: "GET"
  }).then(res2 =>
    res2.json().then(data => {
      //console.log(data)
      changeset.version = Number(data);
      firstdoc();
      rqnewestdoc();
      console.log(changeset.version);
    })
  );
}

//发送changeset
function sendData(changeset) {
  if (changeset.actions.length !== 0) {
    console.log(changeset.actions);
    fetch("/root/first trial/merge", {
      method: "POST",
      body: JSON.stringify(changeset)
    }).then(res => {
      res.json().then(data => {
        console.log(Boolean(changeset.actions.length === 0));
        if (changeset.actions === []) {
          doc.value = localApply(data, doc.value);
        }
      });
    });
    changeset.actions = new Array();
    changeset.version++;
  } else rqnewestdoc();
}

function localApply(actions, temp) {
  console.log("mmmm");
  text = temp;
  actions.forEach(element => {
    if ((element.type = "insert"))
      text =
        text.slice(0, element.index) +
        element.content +
        text.slice(element.index);
    else if ((element.type = "delete"))
      text = text.slice(0, element.index - 1) + text.slice(element.index);
  });
  return text;
}

function localFollow(actionA, actionB) {
  if (actionA === null || actionB === null);
  else if (actionA.type == "insert" && actionB.type === "insert") {
    if (actionA.index > actionB.index);
    else actionB.index--;
  } else if (actionA.type === "insert" && actionB.type === "delete") {
    if (actionA.index < actionB.index) actionB.index++;
    else;
  } else if (action.type === "delete" && action.type === "insert") {
    if (actionA.index > actionB.index);
    else actionB.index--;
  } else if (actionA.type === "delete" && actionB.type === "delete") {
    if (actionA.index > actionB.index);
    else if (actionA.indec > actionB.index) actionB.index--;
    else actionB = null;
  }
  return actionB;
}

function localOT(actionsA, actionsB) {
  A_prime = [];
  temp = actionsA.slice();
  temp.forEach(action => {
    temp_action = action === null ? null : JSON.parse(JSON.stringify(action));
    temp2 = [];
    temp.unshift(temp_action);
    result = temp.reduce((actionA, actionB) => {
      temp_actionA =
        actionA === null ? null : JSON.parse(JSON.stringify(actionA));
      temp_actionB =
        actionB === null ? null : JSON.parse(JSON.stringify(actionB));
      temp2.append(localfollow(temp_actionB, temp_actionB));
      return follow(temp_actionA, temp_actionB);
    });
    A_prime.append(result);
    temp = temp2;
  });
  B_prime = temp2;
  return [A_prime, B_prime];
}

setInterval(function() {
  sendData(changeset);
}, 500)
*/

async function load(){
    let res = await fetch("/api/issues");
    let data = await res.json();

    let total = data.length;
    let pending = data.filter(i=>i.status==="Pending").length;
    let resolved = data.filter(i=>i.status==="Resolved").length;

    document.getElementById("total").innerText = total;
    document.getElementById("pending").innerText = pending;
    document.getElementById("resolved").innerText = resolved;

    // CATEGORY COUNT
    let categoryCount = {};
    data.forEach(i=>{
        categoryCount[i.category] = (categoryCount[i.category]||0)+1;
    });

    new Chart(document.getElementById("categoryChart"),{
        type:"bar",
        data:{
            labels:Object.keys(categoryCount),
            datasets:[{data:Object.values(categoryCount)}]
        }
    });

    // PRIORITY
    let priorityCount = {};
    data.forEach(i=>{
        priorityCount[i.priority]=(priorityCount[i.priority]||0)+1;
    });

    new Chart(document.getElementById("priorityChart"),{
        type:"pie",
        data:{
            labels:Object.keys(priorityCount),
            datasets:[{data:Object.values(priorityCount)}]
        }
    });

    // STATUS
    new Chart(document.getElementById("statusChart"),{
        type:"doughnut",
        data:{
            labels:["Pending","Resolved"],
            datasets:[{data:[pending,resolved]}]
        }
    });
}

load();
async function report(){
    let res = await fetch("/api/report",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
            title: title.value,
            location: location.value,
            category: category.value,
            priority: priority.value
        })
    });

    let data = await res.json();

    if(data.msg === "submitted"){
        document.getElementById("popup").style.display = "flex";
    }
}

    document.getElementById("popup").style.display="flex";
}
async function load(){
    let res = await fetch("/api/issues");
    let data = await res.json();

    let list = document.getElementById("list");
    list.innerHTML = "";

    data.forEach(i=>{
        if(i.user){   // only show user's own
            list.innerHTML += `
            <div class="card">
            <b>${i.title}</b><br>
            ${i.location}<br>
            Status: ${i.status}
            </div>`;
        }
    });
}
async function login(){
    let username = document.getElementById("user").value;
    let password = document.getElementById("pass").value;

    let res = await fetch("/api/login",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({username,password})
    });

    let data = await res.json();

    if(data.msg==="success"){
        window.location="/dashboard";
    } else {
        alert("Wrong password");
    }
}
window.onload = load;
function closePopup(){
    document.getElementById("popup").style.display="none";
}
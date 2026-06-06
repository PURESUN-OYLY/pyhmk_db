// function deleteRow(itemId) {
//     fetch('/delete_item', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify({ id: itemId })
//     })
//         .then(response => response.json())
//         .then(data => {
//             if (data.status === 'success') {
//                 
//                 const alertBox = document.getElementById('alert-box');
//                 alertBox.innerText = data.message;
//                 alertBox.style.display = 'block';

//                
//                 const row = document.getElementById('row-' + itemId);
//                 if (row) row.remove();

//                
//                 setTimeout(() => { alertBox.style.display = 'none'; }, 3000);
//             } else {
//                 alert('Error: ' + data.message);
//             }
//         })
//         .catch(err => console.error('请求失败:', err));
// }

// show toast at bottom-start window
function show_toast(message, type) {
    const Toast = Swal.mixin({
        toast: true,
        position: 'bottom-start',
        showConfirmButton: true,
        timer: 4000,
        timerProgressBar: true,
    });

    Toast.fire({
        icon: type,
        title: message
    });
}

// show message at middle window
function show_message(title, message, type) {
    Swal.fire({
        title: title,
        text: message,
        icon: type,
        confirmButtonText: 'OK'
    });
}

// goto page
function goto_page(url) {
    window.location.href = url;
}
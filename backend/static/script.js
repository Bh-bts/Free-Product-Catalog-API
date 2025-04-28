const data = {
    listProducts: {
        label: "Get All Products",
        method: "GET",
        request: "/get-products",
        response: [
            { "description": "Latest Samsung smartphone", "id": 1, "name": "Samsung s24", "price": 999 },
            { "description": "Latest Apple smartphone", "id": 2, "name": "iPhone 16", "price": 999 }
        ]
    },
    addProducts: {
        label: "Add Product",
        method: "POST",
        request: "/add-product",
        payload: {
            "name": "iPhone 16",
            "description": "Latest Apple smartphone",
            "price": 999
        },
        response: {
            "message": "Product added successfully",
            "product": {
                "id": 2,
                "name": "iPhone 16",
                "description": "Latest Apple smartphone",
                "price": 999
            }
        }
    },
    getSingleProduct: {
        label: "Get Single Product Details",
        method: "GET",
        request: "/product/1",
        response: {
            "description": "Latest Apple smartphone",
            "id": 3,
            "name": "iPhone 18",
            "price": 999
        }
    },
    deleteProduct: {
        label: "Delete Product",
        method: "DELETE",
        request: "/delete-product/1",
        response: { "message": "Product deleted successfully" }
    },
    updateFullProduct: {
        label: "Update Full Product",
        method: "PUT",
        request: "/update-product",
        payload: {
            "price": 999,
            "id": 3,
            "name": "iPhone 17",
            "description": "Latest Apple smartphone"
        },
        response: {
            "message": "Product updated successfully",
            "product": { "id": 3, "name": "iPhone 16", "description": "Latest Apple smartphone", "price": 999 }
        }
    },
    updateProduct: {
        label: "Update Product",
        method: "PATCH",
        request: "/update-product",
        payload: {
                "id": 1,
                "updated_fields": {
                    "price": 1199
                }
        },
        response: {
            "message": "Product partially updated",
            "product": { "id": 1, "name": "iPhone 18", "description": "Latest Apple smartphone", "price": 1999 }
        }
    },
    registerUser: {
        label: "Register User",
        method: "POST",
        request: "/register",
        payload: {
            "username": "John",
            "password": "John@1234"
        },
        response: {
            "message": "User registered successfully",
            "user": { "id": 2, "username": "John" }
        }
    },
    registerUnsuccessful: {
        label: "Register - Unsuccessful",
        method: "POST",
        request: "/register",
        payload: {
            "username": "John1"
        },
        response: {
            "error": "Missing password"
        }
    },
    loginUser: {
        label: "Login User",
        method: "POST",
        request: "/login",
        payload: {
            "username": "John",
            "password": "John@1234"
        },
        response: {
            "message": "Login successful"
        }
    },
    loginUnsuccessful: {
        label: "Login - Unsuccessful",
        method: "POST",
        request: "/login",
        payload: {
            "username": "John1"
        },
        response: {
            "error": "Missing password"
        }
    }
};

// Dynamically create sidebar buttons
const sidebar = document.getElementById('sidebar');

Object.keys(data).forEach(key => {
    const action = data[key];
    const div = document.createElement('div');
    div.className = "flex items-center space-x-4 cursor-pointer hover:bg-purple-100 p-2 rounded";

    div.onclick = () => showData(key);

    const button = document.createElement('button');
    button.className = "bg-purple-500 text-white w-16 text-center px-2 py-1 text-sm rounded";
    button.textContent = action.method;

    const span = document.createElement('span');
    span.className = "text-left";
    span.textContent = action.label;

    div.appendChild(button);
    div.appendChild(span);
    sidebar.appendChild(div);
});

showData(Object.keys(data)[0]);

// Show selected API details
function showData(actionKey) {
    const { request, payload, response } = data[actionKey];

    const baseUrl = window.location.origin;
    const fullUrl = baseUrl + request;

    const requestBox = document.getElementById('requestBox');
    requestBox.innerHTML = `
        <span class="text-blue-600 underline cursor-pointer hover:text-blue-800" onclick="copyToClipboard('${fullUrl}')">
            ${request}
        </span>
    `;

    const payloadBox = document.getElementById('payloadBox');
    payloadBox.textContent = payload ? JSON.stringify(payload, null, 4) : "No payload for this request";

    const responseBox = document.getElementById('responseBox');
    responseBox.textContent = JSON.stringify(response, null, 4);
}

// Helper function to copy text
function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
        .then(() => {
            console.log('Copied:', text);
        })
        .catch(err => {
            console.error('Failed to copy!', err);
        });
}

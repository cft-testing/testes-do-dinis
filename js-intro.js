// ============================================
// JavaScript Introduction - Basic Syntax & Style
// ============================================

// 1. VARIABLES - Three ways to declare variables
// ============================================

// const - Cannot be reassigned (use this by default)
const name = "Alice";
const age = 25;

// let - Can be reassigned (use when value needs to change)
let score = 0;
score = 10; // This is allowed

// var - Old way (avoid using, has confusing scope rules)
var oldStyle = "not recommended";


// 2. DATA TYPES
// ============================================

// String - text in quotes
const greeting = "Hello, World!";
const message = 'Single quotes work too';

// Number - integers and decimals
const integer = 42;
const decimal = 3.14;

// Boolean - true or false
const isActive = true;
const isCompleted = false;

// Array - ordered list of values
const colors = ["red", "green", "blue"];
const numbers = [1, 2, 3, 4, 5];

// Object - key-value pairs
const person = {
  name: "Bob",
  age: 30,
  city: "New York"
};

// null and undefined
const empty = null;
let notDefined; // undefined by default


// 3. FUNCTIONS
// ============================================

// Function declaration
function greet(userName) {
  return "Hello, " + userName + "!";
}

// Arrow function (modern style)
const add = (a, b) => {
  return a + b;
};

// Short arrow function (implicit return)
const multiply = (a, b) => a * b;

// Calling functions
console.log(greet("Alice")); // "Hello, Alice!"
console.log(add(5, 3));      // 8
console.log(multiply(4, 2)); // 8


// 4. STRINGS & TEMPLATE LITERALS
// ============================================

const firstName = "John";
const lastName = "Doe";

// Old way - concatenation
const fullName = firstName + " " + lastName;

// Modern way - template literals (backticks)
const fullNameModern = `${firstName} ${lastName}`;
const ageMessage = `I am ${age} years old`;


// 5. ARRAYS - Common operations
// ============================================

const fruits = ["apple", "banana", "orange"];

// Access by index (starts at 0)
console.log(fruits[0]); // "apple"

// Array methods
fruits.push("grape");        // Add to end
fruits.pop();                // Remove from end
fruits.length;               // Get length

// Looping through arrays
fruits.forEach(fruit => {
  console.log(fruit);
});

// Map - transform each element
const upperFruits = fruits.map(fruit => fruit.toUpperCase());

// Filter - keep elements that match condition
const longFruits = fruits.filter(fruit => fruit.length > 5);


// 6. OBJECTS - Working with data
// ============================================

const car = {
  brand: "Toyota",
  model: "Camry",
  year: 2022,
  // Method (function inside object)
  getInfo: function() {
    return `${this.brand} ${this.model} (${this.year})`;
  }
};

// Accessing properties
console.log(car.brand);        // Dot notation
console.log(car["model"]);     // Bracket notation

// Adding/modifying properties
car.color = "blue";
car.year = 2023;


// 7. CONTROL FLOW - if/else
// ============================================

const temperature = 25;

if (temperature > 30) {
  console.log("It's hot!");
} else if (temperature > 20) {
  console.log("It's nice!");
} else {
  console.log("It's cold!");
}

// Ternary operator (short if/else)
const weather = temperature > 25 ? "warm" : "cool";


// 8. LOOPS
// ============================================

// for loop
for (let i = 0; i < 5; i++) {
  console.log(i); // 0, 1, 2, 3, 4
}

// while loop
let count = 0;
while (count < 3) {
  console.log(count);
  count++;
}

// for...of loop (iterate over arrays)
for (const fruit of fruits) {
  console.log(fruit);
}


// 9. COMPARISON & LOGICAL OPERATORS
// ============================================

// Comparison
console.log(5 === 5);    // true (strict equality)
console.log(5 == "5");   // true (loose equality, avoid this)
console.log(5 !== 3);    // true (not equal)
console.log(10 > 5);     // true

// Logical operators
console.log(true && false);  // false (AND)
console.log(true || false);  // true (OR)
console.log(!true);          // false (NOT)


// 10. MODERN JAVASCRIPT FEATURES
// ============================================

// Destructuring - extract values from objects/arrays
const user = { username: "alice", email: "alice@example.com" };
const { username, email } = user;

const [first, second] = colors;

// Spread operator - copy/combine arrays and objects
const moreFruits = [...fruits, "mango", "kiwi"];
const userWithAge = { ...user, age: 28 };

// Default parameters
const greetWithDefault = (name = "Guest") => {
  return `Hello, ${name}!`;
};


// 11. COMMON PATTERNS
// ============================================

// Check if value exists (truthy/falsy)
const value = "something";
if (value) {
  console.log("Value exists");
}

// Optional chaining - safely access nested properties
const profile = { user: { name: "Alice" } };
console.log(profile?.user?.name); // "Alice"
console.log(profile?.address?.street); // undefined (no error)

// Nullish coalescing - default values
const userInput = null;
const result = userInput ?? "default value";


// 12. PRACTICAL EXAMPLE - Putting it all together
// ============================================

// Create a simple todo list manager
const createTodoList = () => {
  const todos = [];

  return {
    add: (task) => {
      todos.push({ task, completed: false });
      console.log(`Added: ${task}`);
    },

    complete: (index) => {
      if (todos[index]) {
        todos[index].completed = true;
        console.log(`Completed: ${todos[index].task}`);
      }
    },

    list: () => {
      console.log("\nTodo List:");
      todos.forEach((todo, index) => {
        const status = todo.completed ? "✓" : " ";
        console.log(`${index + 1}. [${status}] ${todo.task}`);
      });
    }
  };
};

// Using the todo list
const myTodos = createTodoList();
myTodos.add("Learn JavaScript basics");
myTodos.add("Build a small project");
myTodos.add("Practice coding daily");
myTodos.complete(0);
myTodos.list();


// ============================================
// TIPS FOR LEARNING JAVASCRIPT
// ============================================

// 1. Use 'const' by default, 'let' when needed, avoid 'var'
// 2. Prefer arrow functions for cleaner syntax
// 3. Use template literals instead of string concatenation
// 4. Learn array methods: map, filter, reduce, forEach
// 5. Use strict equality (===) instead of loose equality (==)
// 6. Practice by building small projects
// 7. Use console.log() frequently to understand what's happening
// 8. Read error messages carefully - they help you learn

console.log("\n🎉 You've completed the JavaScript introduction!");

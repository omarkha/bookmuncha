<template>
    <div class="container">
      <div class="upload-section">
        <input type="file" id="fileInput" @change="uploadFile" />
        <button @click="askQuestion">Ask Question</button>
      </div>
      
      <div v-if="answers.length" class="answers-section">
        <h2>Answers:</h2>
        <ul>
          <li v-for="(answer, index) in answers" :key="index">{{ answer.text }}</li>
        </ul>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  
  export default {
    data() {
      return {
        file: null,
        answers: []
      };
    },
    methods: {
      async uploadFile(event) {
        this.file = event.target.files[0];
        let formData = new FormData();
        formData.append("file", this.file);
  
        let response = await axios.post("https://bookmuncha.onrender.com/api/upload", formData);
  
        this.answers = response.data.chunks;
      },
      async askQuestion() {
        let response = await axios.post("https://bookmuncha.onrender.com/api/answer", {
          question: "What is this book about?",
          chunks: this.answers
        });
  
        this.answers = response.data.answers;
      }
    }
  };
  </script>
  
  <style scoped>
  .container {
    max-width: 600px;
    margin: 40px auto;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #f9f9f9;
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  }
  
  .upload-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
  }
  
  input[type="file"] {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    cursor: pointer;
  }
  
  button {
    padding: 10px 15px;
    border: none;
    background-color: #007bff;
    color: white;
    font-size: 16px;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.3s ease;
  }
  
  button:hover {
    background-color: #0056b3;
  }
  
  .answers-section {
    margin-top: 20px;
  }
  
  h2 {
    color: #333;
  }
  
  ul {
    list-style: none;
    padding: 0;
  }
  
  li {
    background: #fff;
    padding: 10px;
    margin-top: 5px;
    border-radius: 4px;
    border-left: 4px solid #007bff;
  }
  </style>
  
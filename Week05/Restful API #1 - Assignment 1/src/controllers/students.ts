import { Hono } from "hono";
import * as StudentService from "../services/students.js";

const app = new Hono();

app.get("/", async (c) => {
  const data = await StudentService.getAllStudents();
  return c.json(data);
});

app.get("/:id", async (c) => {
  const id = parseInt(c.req.param("id"));
  const data = await StudentService.getStudentById(id);
  if (!data) return c.json({ error: "Student not found" }, 404);
  return c.json(data);
});

app.post("/", async (c) => {
  const body = await c.req.json();
  const newData = await StudentService.createStudent(body);
  return c.json(newData, 201);
});

app.put("/:id", async (c) => {
  const id = parseInt(c.req.param("id"));
  const body = await c.req.json();
  const updatedData = await StudentService.updateStudent(id, body);
  if (!updatedData) return c.json({ error: "Student not found" }, 404);
  return c.json(updatedData);
});

app.delete("/:id", async (c) => {
  const id = parseInt(c.req.param("id"));
  const deletedData = await StudentService.deleteStudent(id);
  if (!deletedData) return c.json({ error: "Student not found" }, 404);
  return c.json({ message: "Student deleted successfully", deletedData });
});

export default app;

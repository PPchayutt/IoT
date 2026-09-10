import { eq } from "drizzle-orm";
import db from "../db/index.js";
import { students } from "../db/schema.js";

export const getAllStudents = async () => {
  return await db.select().from(students);
};

export const getStudentById = async (id: number) => {
  const result = await db.select().from(students).where(eq(students.id, id));
  return result[0];
};

export const createStudent = async (data: any) => {
  const result = await db.insert(students).values(data).returning();
  return result[0];
};

export const updateStudent = async (id: number, data: any) => {
  const result = await db
    .update(students)
    .set(data)
    .where(eq(students.id, id))
    .returning();
  return result[0];
};

export const deleteStudent = async (id: number) => {
  const result = await db
    .delete(students)
    .where(eq(students.id, id))
    .returning();
  return result[0];
};

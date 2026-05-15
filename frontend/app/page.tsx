/// <reference types="react" />
import React from "react"

async function getJobs() {
  const response = await fetch("http://localhost:8000/jobs", {
    cache: "no-store",
  })

  return response.json()
}

export default async function Home() {
  const jobs = await getJobs()

  return (
    <main className="p-10">
      <h1 className="text-4xl font-bold mb-8">
        Alternances Cybersécurité Lille
      </h1>

      <div className="grid gap-4">
        {jobs.map((job: any) => (
          <div
            key={job.id}
            className="border rounded-xl p-4" >
            <h2 className="font-bold text-xl">
              {job.title}
            </h2>

            <p>{job.company}</p>
            <p>{job.city}</p>

            <a
              href={job.url}
              target="_blank"
              className="text-blue-500"
            >
              Voir l'offre
            </a>
          </div>
        ))}
      </div>
    </main>
  )
}
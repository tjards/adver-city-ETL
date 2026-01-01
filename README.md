## Dev notes

- after ingestion and sampling done, build a new notebook for efficient sampling
- exploration and data ingestion reuse a lot of the same concepts, after pipeline is built, get exploration to use the better methods
- now, you are downloading raw, then sampling; build a pipeline that pulls raw, samples, and deletes what is not needed
- when referencing what is needed, refer sampled, not raw (as raw will be the biggest)
- there;s room for pipeline to be interrupted by a bad filename; encourage it to pass to next instead of stopping
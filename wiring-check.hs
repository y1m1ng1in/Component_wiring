-- Copyright © 2011 Bart Massey
-- [This program is licensed under the "MIT License"]
-- Please see the file COPYING in the source
-- distribution of this software for license terms.

-- | Check a wiring solution for validity.

import Control.Monad (unless, mapM_)
import Data.Array
import Data.List (sort, transpose)
import System.Environment (getArgs)
import Text.Printf

-- | Read in an instance, producing a connectivity matrix.
readInstance :: String -> (Int, Array (Int, Int) Bool)
readInstance desc =
  let rows = lines desc in
  let n = length rows
      syms = concatMap (map val) rows in
  (n, listArray ((1, 1), (n, n)) syms)
  where
    val 't' = True
    val 'f' = False
    val _ = error "unexpected symbol in matrix"


-- | Read a solution into a 2 x n matrix.
readSoln :: String -> (Int, Array (Int, Int) Int)
readSoln desc =
  let rows = lines desc in
  let n = length rows
      syms = concat $ transpose $ map (map read . words) rows in
  (n, listArray ((1, 1), (2, n)) syms)

-- | Make sure the solution is legal. Check that
-- each column is a permutation of 1..n, and that
-- no wires cross.
check n inst soln = do
  mapM_ checkCol [1, 2]
  let wires = map snd $ filter fst $ 
              [(inst ! (soln ! (1, i), soln ! (2, j)), (i, j)) |
               i <- [1..n], j <- [1..n]]
  mapM_ (checkWire wires) wires
  where
    checkCol :: Int -> IO ()
    checkCol i = do
      let col = [ soln ! (1, i) | i <- [1..n] ]
      unless (sort col == [1..n]) $ 
        error $ printf "column %d is not an input permutation" i
    checkWire wires (i, j) = do
      mapM_ uncrossing wires
      where
        uncrossing (i', j')
          | (i' <= i && j' <= j) || (i' >= i && j' >= j) = return ()
          | otherwise = do
            let m = soln ! (1, i)
            let n = soln ! (2, j)
            let m' = soln ! (1, i')
            let n' = soln ! (2, j')
            error $ printf "wire %d-%d crossed by wire %d-%d" m n m' n'

-- | This simple driver reads in the instance, reads in
-- the proposed solution, and checks the solution.
main = do
  [instFile, solnFile] <- getArgs
  instDesc <- readFile instFile
  let (n, inst) = readInstance instDesc
  solnDesc <- readFile solnFile
  let (n', soln) = readSoln solnDesc
  unless (n == n') $ error "soln and problem sizes differ"
  check n inst soln
  putStrLn "OK"

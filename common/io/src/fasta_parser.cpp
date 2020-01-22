/*
* Copyright (c) 2019, NVIDIA CORPORATION.  All rights reserved.
*
* NVIDIA CORPORATION and its licensors retain all intellectual property
* and proprietary rights in and to this software, related documentation
* and any modifications thereto.  Any use, reproduction, disclosure or
* distribution of this software and related documentation without an express
* license agreement from NVIDIA CORPORATION is strictly prohibited.
*/

#include "hts_fasta_parser.hpp"
#include "kseqpp_fasta_parser.hpp"

#include "claragenomics/io/fasta_parser.hpp"

#include <memory>
#include <vector>

namespace claragenomics
{
namespace io
{

std::unique_ptr<FastaParser> create_hts_fasta_parser(const std::string &fasta_file)
{
    return std::make_unique<FastaParserHTS>(fasta_file);
}

std::shared_ptr<FastaParser> create_kseq_fasta_parser(const std::string& fasta_file)
{
    return std::make_unique<FastaParserKseqpp>(FastaParserKseqpp(fasta_file));
}

} // namespace io
} // namespace claragenomics

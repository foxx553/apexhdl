############################################################################################
# ApexHDL: A Tool for Generating/Benchmarking Unary and Binary Function Evaluators on FPGA #
# Copyright (C) 2026 Florian Delhon                                                        # 
#                                                                                          #
# This program is free software: you can redistribute it and/or modify                     #
# it under the terms of the GNU General Public License as published by                     #
# the Free Software Foundation, either version 3 of the License, or                        #
# (at your option) any later version.                                                      #
#                                                                                          #
# This program is distributed in the hope that it will be useful,                          #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                           #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                            #
# GNU General Public License for more details.                                             #
#                                                                                          #
# You should have received a copy of the GNU General Public License                        #
# along with this program.  If not, see <https://www.gnu.org/licenses/>.                   #
############################################################################################

from typing import Any

from apex.runner import Runner

# Main function
def main():
    """
    Main function, entry point of the ApexHDL code
    """

    # Parsing args
    runner: Runner = Runner()
    args_dict: dict[str, Any] = runner.build_dict()

    # Running pipeline(s)
    runner.run(args_dict)

# Entry point
if __name__ == "__main__":
    main()